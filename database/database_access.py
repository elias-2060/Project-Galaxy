from functools import wraps
from typing import Any, Callable, TypeVar
import sys
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, object_session, sessionmaker

from database.config import config_data


# Makes a base for all the table classes to derive from
class Base(DeclarativeBase):
    pass


# Takes all the data from the config
database: str = config_data["db_name"]
username: str = config_data["db_user"]
port: int = config_data["db_port"]
host: str = config_data["db_host"]
password: str = config_data["db_password"]

# We connect to the database and create and engine with a session where we are going to be working
db_url = (
    "sqlite:///:memory:"
    if "pytest" in sys.modules  # use in-memory database when running tests
    else f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
)

engine: Engine = create_engine(db_url, echo=False, pool_pre_ping=True)
DefaultSession = sessionmaker(bind=engine)


RT = TypeVar("RT")


def doublewrap(f):
    """
    from: https://stackoverflow.com/questions/653368/how-to-create-a-decorator-that-can-be-used-either-with-or-without-parameters
    a decorator decorator, allowing the decorator to be used as:
    @decorator(with, arguments, and=kwargs)
    or
    @decorator
    """

    @wraps(f)
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            return f(args[0])
        else:
            return lambda realf: f(realf, *args, **kwargs)

    return new_dec


@doublewrap
def auto_session(_func: Callable[..., RT], /, *, add_all=True, auto_commit=False):
    """
    Ensure a call to the function always has a :class:`flask.orm.Session`.
    If a session is provided it will be forwarded to the function.
    Else if the function is an instance method it will try to use the session the object is already associated.
    As a last resort a new session will be created for the function to run in which is closed once the function end.

    :param _func: The function to wrap. ! Don't pass manually, passed automatically by the wrapping process
    :param add_all: Whether to add all orm class instances to the session
    :param auto_commit: Whether to commit the session when the function returns

    .. note::
       All wrapped functions must declare a ``session`` parameter.
    """

    # indicator if the function does not ask for a session
    func_requires_session: bool = "session" in _func.__code__.co_varnames

    @wraps(_func)
    def wrapper(*args, force_auto_commit: bool = None, force_add_all: bool = None, **kwargs) -> RT:
        add_all_enabled: bool = (add_all and force_add_all is None) or force_add_all
        auto_commit_enabled: bool = (auto_commit and force_auto_commit is None) or force_auto_commit

        def run_func(session: Session, inject_session: bool = True) -> RT:
            """
            Run the provided function with the most appropriate session.
            :param session: The session to use
            :param inject_session: Whether to inject the session
            :return: The result of the function
            """
            if inject_session and func_requires_session:  # inject the session into the keyword arguments
                kwargs["session"] = session

            if add_all_enabled:  # if enabled add all orm instances to the session
                session.add_all(instances)

            res: RT = _func(*args, **kwargs)

            if auto_commit_enabled:  # if enabled commit the session when the function returns
                session.commit()

            return res

        if add_all_enabled:  # if enabled create a list of all orm class instances
            instances = [arg for arg in [*args, *kwargs.values()] if isinstance(arg, DeclarativeBase)]

        # extract session from function arguments
        if "session" in _func.__code__.co_varnames:
            session_index = _func.__code__.co_varnames.index("session")
            session = args[session_index] if session_index < len(args) else kwargs.get("session")
        else:
            session = kwargs.get("session")

        # if the function doesn't ask for a session, remove it from the keyword arguments
        if not func_requires_session:
            kwargs.pop("session", None)

        # if use the provided session if possible
        if session is not None:
            assert isinstance(session, Session), "session must be of type 'Session'"
            return run_func(session, inject_session=False)

        # check if the function is an instance method, the instance will always be added to the session
        # * this code assumes a method is an instance method if it's first argument is called `self`
        if _func.__code__.co_varnames[0] == "self":
            # try to use the session the object is already in
            session: Session | None = object_session(args[0])  # first argument is always `self` for instances
            if session is not None:
                return run_func(session)

            # create a new session context for the call
            with DefaultSession() as session:
                session.add(args[0])
                return run_func(session)

        # create a new session context for the call
        with DefaultSession() as session:
            return run_func(session)

    return wrapper


def default_factory(**defaults) -> Callable:
    """
    Set default values with a factory function.
    If a value is already provided, it will be forwarded instead.
    """

    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args, **kwargs) -> Any:
            # generate and set all default values that were not provided
            for arg, gen in defaults.items():
                if arg not in kwargs and arg not in func.__code__.co_varnames[0 : len(args)]:
                    kwargs[arg] = gen()
            return func(*args, **kwargs)

        return inner

    return wrapper
