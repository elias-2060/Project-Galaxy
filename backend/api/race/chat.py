from http import HTTPStatus

from flask import Response, request
from flask import session as flask_session
from flask_restx import Resource, fields, marshal

from backend.api.race import api
from backend.game_classes import User
from backend.game_classes.Message import MAX_MESSAGE_LENGTH, Message
from database.database_access import DefaultSession

message_model = api.model(
    "ChatMessage",
    {
        "message_id": fields.String(
            description="Id of the message",
            required=True,
            nullable=False,
            attribute=lambda m: str(m.message_id),
        ),
        "user_id": fields.String(
            description="Id of the user that posted the message",
            required=True,
            nullable=False,
            attribute=lambda m: str(m.user_id),
        ),
        "user_name": fields.String(
            description="Name of the user that posted the message",
            required=True,
            nullable=False,
            attribute=lambda m: m.user.user_name,
        ),
        "race_id": fields.String(
            description="Id of the race the messages was posted in",
            required=True,
            nullable=False,
            attribute=lambda m: str(m.race_id),
        ),
        "position": fields.Integer(
            description="Order of the message in the chat",
            required=True,
            nullable=False,
        ),
        "message": fields.String(
            description="The message content",
            required=True,
            nullable=False,
        ),
    },
)
messages_model = api.model(
    "ChatMessages",
    {
        "messages": fields.List(
            fields.Nested(message_model),
            required=True,
        ),
    },
)
update_messages_model = api.clone(
    "UpdateChatMessages",
    messages_model,
    {
        "deleted_messages": fields.List(
            fields.Nested(message_model),
        ),
    },
)

get_chat_parser = api.parser().add_argument("start_from", type=int)
post_chat_parser = api.parser().add_argument("message", type=str, required=True)  # , location="data"
post_chat_model = api.model("postChat", {"message": fields.String(description="Message content", required=True)})
delete_chat_parser = api.parser().add_argument("message_id", type=str, required=True)


@api.route("/chat")
class Chat(Resource):
    @api.expect(get_chat_parser)
    @api.response(HTTPStatus.OK, "All chat messages", messages_model)
    @api.response(HTTPStatus.NOT_MODIFIED, "No new messages")
    @api.response(HTTPStatus.PARTIAL_CONTENT, "New chat messages", update_messages_model)
    @api.response(HTTPStatus.NOT_FOUND, "User not in race")
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    def get(self):
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            return api.abort(HTTPStatus.UNAUTHORIZED, "User not logged in")

        data = get_chat_parser.parse_args(request)
        with DefaultSession() as session:
            user: User | None = User.load_by_name(user_name, session=session)
            if user.race is None:
                return api.abort(HTTPStatus.NOT_FOUND, "User not in race")

            if data["start_from"] is not None:
                last_message_position = Message.last_position(user.race_id)
                if last_message_position == data["start_from"]:
                    return Response(status=HTTPStatus.NO_CONTENT)

                messages: list[Message] = Message.load_range(
                    user.race_id, data["start_from"], last_message_position+1, session=session
                )
                return marshal({"messages": messages}, messages_model), HTTPStatus.PARTIAL_CONTENT
            else:
                messages: list[Message] = user.race.get_messages()
                return marshal({"messages": messages}, messages_model), HTTPStatus.OK

    @api.expect(post_chat_parser)
    @api.response(HTTPStatus.CREATED, "Posted message", message_model)
    @api.response(HTTPStatus.NOT_FOUND, "User not in race")
    @api.response(HTTPStatus.BAD_REQUEST, "Message too long")
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    def post(self):
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            return api.abort(HTTPStatus.UNAUTHORIZED, "User not logged in")

        data = post_chat_parser.parse_args(request)
        with DefaultSession() as session:
            user = User.load_by_name(user_name, session=session)
            if user.race is None:
                return api.abort(HTTPStatus.NOT_FOUND, "User not in race")

            if len(data["message"]) > MAX_MESSAGE_LENGTH:
                return api.abort(HTTPStatus.BAD_REQUEST, "Message too long")

            message = Message(
                message=data["message"],
                user_id=user.user_id,
                race_id=user.race_id,
                position=Message.last_position(user.race_id) + 1,
            )

            session.add(message)
            session.commit()
            return marshal(message, message_model), HTTPStatus.CREATED

    @api.expect(delete_chat_parser)
    @api.response(HTTPStatus.OK, "Message deleted")
    @api.response(HTTPStatus.BAD_REQUEST, "User did not send the message")
    @api.response(HTTPStatus.NOT_FOUND, "User not in race or message not found")
    @api.response(HTTPStatus.UNAUTHORIZED, "User not logged in")
    def delete(self):
        user_name = flask_session.get("user_name", None)
        if user_name is None:
            return api.abort(HTTPStatus.UNAUTHORIZED, "User not logged in")

        data = delete_chat_parser.parse_args(request)
        with DefaultSession() as session:
            user = User.load_by_name(user_name, session=session)
            if user.race is None:
                return api.abort(HTTPStatus.NOT_FOUND, "User not in race")

            message = Message.load_by_id(data["message_id"], session=session)
            if message is None:
                return api.abort(HTTPStatus.NOT_FOUND, "Message not found")

            if message.user_id != user.user_id:
                return api.abort(HTTPStatus.BAD_REQUEST, "User did not send the message")

            session.delete(message)
            session.commit()
            return Response("Message deleted", HTTPStatus.OK)
