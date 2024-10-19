package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"os"
	"os/exec"
	"github.com/op/go-logging"
)

const keyServerAddr string = "serverAddr"

// set the authentication token
var PORT, PORT_FOUND = os.LookupEnv("PORT")

// set the authentication token
var ADDR, ADDR_FOUND = os.LookupEnv("ADDR")

// set the authentication token
var AUTH_TOKEN, AUTH_TOKEN_FOUND = os.LookupEnv("AUTH_TOKEN")

// set the deployment script
var DEPLOY_SCRIPT, DEPLOY_SCRIPT_FOUND = os.LookupEnv("DEPLOY_SCRIPT")

// create logger
var log = logging.MustGetLogger("project-galaxy-autodeploy-logger")
var format = logging.MustStringFormatter(`%{color}%{time:15:04:05.000} %{shortfunc} ▶ %{level:.4s} %{id:03x}%{color:reset} %{message}`)

// catch-all route
func getRoot(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusNotFound)
	io.WriteString(w, "Nothing to see here -_-\n")
	log.Debugf("got request to %v\n", r.URL)
}

type PullReqInfo struct {
	Action      string `json:"action"`
	PullRequest struct {
		Merged bool `json:"merged"` // merge state
		Base struct { // branch merged into
			Ref string `json:"ref"` // branch name
		} `json:"base"`
	} `json:"pull_request"`
}

func getRedeploy(w http.ResponseWriter, r *http.Request) {
	// get the auth-token attribute from the request
	hasToken := r.URL.Query().Has("auth-token")
	token := r.URL.Query().Get("auth-token")

	// stop if token is missing
	if !hasToken {
		w.WriteHeader(http.StatusUnprocessableEntity)
		io.WriteString(w, "No auth token provided\n")
		log.Debug("Got request without auth token\n")
		return
	}

	// stop if token doesn't match
	if token != AUTH_TOKEN {
		w.WriteHeader(http.StatusUnauthorized)
		io.WriteString(w, "Invalid token\n")
		log.Debug("Got request with invalid token\n")
		return
	}

	body, b_err := io.ReadAll(r.Body)
	if b_err != nil {
		w.WriteHeader(http.StatusBadRequest)
		io.WriteString(w, fmt.Sprintf("Invalid json: %v\n", b_err))
		log.Debugf("Invalid json: %v\n", b_err)
		return
	}
	log.Debug("got body:\n", string(body))

	// unmarshal json body into struct
	var pri PullReqInfo
	err := json.NewDecoder(bytes.NewReader(body)).Decode(&pri)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		io.WriteString(w, fmt.Sprintf("Invalid json: %v\n", err))
		log.Debugf("Invalid json: %v\n", err)
		return
	}
	log.Debugf("Relevant pull request info: %v\n", pri)

	// verify the pr action is a merge to the production branch
	if pri.Action != "closed" || pri.PullRequest.Merged != true || pri.PullRequest.Base.Ref != "production" {
		w.WriteHeader(http.StatusOK)
		io.WriteString(w, "Unapplicable PR action\n")
		log.Debugf("Got unapplicable pull request action\n")
		return
	}

	log.Notice("Redeploying...\n")
	// run deployment script
	cmd := exec.Command(DEPLOY_SCRIPT)
	output, c_err := cmd.Output()

	// if command failed to run there is no hope of recovery. So stop the server
	if c_err != nil {
		w.WriteHeader(http.StatusInternalServerError) // TODO proper status code
		log.Errorf("Failed to run command {%v}. Is the deployment script missing?\n", c_err)
		return
	}
	log.Info("Deployment output:\n", string(output))

	// send success
	w.WriteHeader(http.StatusOK)
	io.WriteString(w, "Redeployed\n")
	log.Notice("Redeployed\n")
}

func main() {
	// set up logger
	logBackend := logging.NewLogBackend(os.Stderr, "", 0)           // create new backend
	logFormatter := logging.NewBackendFormatter(logBackend, format) // add formatting to backend
	logLeveled := logging.AddModuleLevel(logFormatter)              // set minimum loglevel
	logLeveled.SetLevel(logging.INFO, "")
	logging.SetBackend(logLeveled)

	// verify that all environment variables are set
	if !ADDR_FOUND {
		log.Fatal("No address provided to bind to\n")
	}
	if !PORT_FOUND {
		log.Fatal("No port provided to bind to\n")
	}
	if !DEPLOY_SCRIPT_FOUND {
		log.Fatal("No deployment script provided to execute\n")
	}
	if !AUTH_TOKEN_FOUND {
		log.Fatal("No authentication token provided...    stopping server...\n")
	}

	// set up router
	var mux *http.ServeMux = http.NewServeMux()
	mux.HandleFunc("/", getRoot)
	mux.HandleFunc("/manage/redeploy", getRedeploy)

	ctx := context.Background()
	// create a new http server
	s := &http.Server{
		Addr:    fmt.Sprintf("%v:%v", ADDR, PORT),
		Handler: mux,
		BaseContext: func(l net.Listener) context.Context {
			ctx = context.WithValue(ctx, keyServerAddr, l.Addr().String())
			return ctx
		},
	}

	// start serving
	log.Infof("Starting server on %v:%v\n", ADDR, PORT)
	err := s.ListenAndServe()
	if errors.Is(err, http.ErrServerClosed) {
		log.Debugf("server closed\n")
	} else if err != nil {
		log.Fatalf("error starting server: %s\n", err)
	}
}
