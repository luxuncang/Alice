from typing import Optional, List, Union

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import Field, SQLModel, create_engine, Relationship, Session, values


class BotlabelLink(SQLModel, table=True):
    bot_id: Optional[int] = Field(default=None, foreign_key="bot.id", primary_key=True)
    label_id: Optional[int]  = Field(default=None, foreign_key="botlabel.id", primary_key=True)

class UserlabelLink(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    label_id: Optional[int]  = Field(default=None, foreign_key="userlabel.id", primary_key=True)

class GrouplabelLink(SQLModel, table=True):
    group_id: Optional[int] = Field(default=None, foreign_key="group.id", primary_key=True)
    label_id: Optional[int]  = Field(default=None, foreign_key="grouplabel.id", primary_key=True)

class EventlabelLink(SQLModel, table=True):
    event_id: Optional[int] = Field(default=None, foreign_key="event.id", primary_key=True)
    label_id: Optional[int]  = Field(default=None, foreign_key="eventlabel.id", primary_key=True)

class RelationLink(SQLModel, table=True):
    relation_id: Optional[int] = Field(default=None, foreign_key="relation.id", primary_key=True)
    context_id: Optional[int]  = Field(default=None, foreign_key="context.id", primary_key=True)

class Context(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    direction: bool = Field(default=True)
    frequency_n: int = Field(default=1)
    frequency_t: int = Field(default=60)
    delayed: int = Field(default=0)
    botlabel_id: Optional[int] = Field(default=None, foreign_key="botlabel.id")
    userlabel_id: Optional[int]  = Field(default=None, foreign_key="userlabel.id")
    grouplabel_id: Optional[int]  = Field(default=None, foreign_key="grouplabel.id")
    eventlabel_id: Optional[int]  = Field(default=None, foreign_key="eventlabel.id")
    relations: List["Relation"] = Relationship(back_populates="contexts", link_model=RelationLink)

class Bot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    botlabels: List["Botlabel"] = Relationship(back_populates="bots", link_model=BotlabelLink)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userlabels: List["Userlabel"] = Relationship(back_populates="users", link_model=UserlabelLink)

class Group(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    grouplabels: List["Grouplabel"] = Relationship(back_populates="groups", link_model=GrouplabelLink)

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    eventlabels: List["Eventlabel"] = Relationship(back_populates="events", link_model=EventlabelLink)

class Botlabel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    bots: List["Bot"] = Relationship(back_populates="botlabels", link_model=BotlabelLink)

class Userlabel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    users: List["User"] = Relationship(back_populates="userlabels", link_model=UserlabelLink)

class Grouplabel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    groups: List["Group"] = Relationship(back_populates="grouplabels", link_model=GrouplabelLink)

class Eventlabel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    events: List["Event"] = Relationship(back_populates="eventlabels", link_model=EventlabelLink)

class Relation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    contexts: List["Context"] = Relationship(back_populates="relations", link_model=RelationLink)

class ModelCore:
    sql_url = "sqlite:///./Alice/db/database.db"
    aync_sql_url = f"sqlite+aiosqlite:///./Alice/db/database.db"

    @classmethod
    def create_engine(cls):
        cls.async_engine = create_async_engine(cls.aync_sql_url)
        # cls.session = AsyncSession(cls.engine)

    @classmethod
    def init_graia(cls, purge: bool = True):
        cls.engine = create_engine(cls.sql_url, echo=False)
        cls.create_engine()
        if purge:
            SQLModel.metadata.drop_all(cls.engine)
            SQLModel.metadata.create_all(cls.engine)

    @classmethod
    def create_label(cls, label: str, name: str, ls: List[Union[Bot, User, Group, Event]], session: Session) -> None:
        if label == "GraiaBot":
            if lb := session.query(Botlabel).where(Botlabel.name == name).first():
                lb.bots = ls + lb.bots
            else:
                res = Botlabel(name=name, bots = ls)
                session.add(res)
        elif label == "GraiaUser":
            if (
                lb := session.query(Userlabel)
                .where(Userlabel.name == name)
                .first()
            ):
                lb.users = ls + lb.users
            else:
                res = Userlabel(name=name, users=ls)
                session.add(res)
        elif label == "GraiaGroup":
            if (
                lb := session.query(Grouplabel)
                .where(Grouplabel.name == name)
                .first()
            ):
                lb.groups = ls + lb.groups
            else:
                res = Grouplabel(name=name, groups=ls)
                session.add(res)
        elif label == "GraiaEvent":
            if (
                lb := session.query(Eventlabel)
                .where(Eventlabel.name == name)
                .first()
            ):
                lb.events = ls + lb.events
            else:
                res = Eventlabel(name=name, events=ls)
                session.add(res)
        else:
            raise Exception("label error")
        session.flush()
        session.commit()

    @classmethod
    def create_graia(cls, label: str, name: Union[str, int], session: Session):
        if label == "GraiaBot":
            if bot := session.query(Bot).where(Bot.id == int(name)).first():
                return bot
            else:
                res = Bot(id = int(name))
        elif label == "GraiaGroup":
            if group := session.query(Group).where(Group.id == int(name)).first():
                return group
            else:
                res = Group(id = int(name))
        elif label == "GraiaUser":
            if user := session.query(User).where(User.id == int(name)).first():
                return user
            else:
                res = User(id = int(name))
        elif label == "GraiaEvent":
            if event := session.query(Event).where(Event.name == name).first():
                return event
            else:
                res = Event(name = name)
        else:
            raise Exception("label is not defined")

        session.add(res)
        session.commit()
        session.refresh(res)
        return res

    @classmethod
    async def add_graia(cls, label: str, name: str, ls: List[Union[Bot, User, Group, Event]]):
        async with AsyncSession(cls.async_engine) as session:
            if label == "GraiaBot":
                if (
                    lb := session.query(Botlabel)
                    .where(Botlabel.name == name)
                    .first()
                ):
                    lb.bots = ls + lb.bots
                else:
                    res = Botlabel(name=name, bots = ls)
                    session.add(res)
            elif label == "GraiaUser":
                if (
                    lb := session.query(Userlabel)
                    .where(Userlabel.name == name)
                    .first()
                ):
                    lb.users = ls + lb.users
                else:
                    res = Userlabel(name=name, users=ls)
                    session.add(res)
            elif label == "GraiaGroup":
                if (
                    lb := session.query(Grouplabel)
                    .where(Grouplabel.name == name)
                    .first()
                ):
                    lb.groups = ls + lb.groups
                else:
                    res = Grouplabel(name=name, groups=ls)
                    session.add(res)
            elif label == "GraiaEvent":
                if (
                    lb := session.query(Eventlabel)
                    .where(Eventlabel.name == name)
                    .first()
                ):
                    lb.events = ls + lb.events
                else:
                    res = Eventlabel(name=name, events=ls)
                    session.add(res)
            else:
                raise Exception("label error")
            session.flush()
            session.commit()

    @classmethod
    def remove_graia(cls, label: str, name: str, value: str):
        with Session(cls.engine) as seesion:
            if label == "GraiaBot":
                lb = seesion.query(Botlabel).where(Botlabel.name == name).first()
                bot = seesion.query(Bot).where(Bot.id == int(value)).first()
                if lb and bot:
                    seesion.delete(seesion.query(BotlabelLink).where(bot_id=bot.id, label_id=lb.id))
            elif label == "GraiaUser":
                lb = seesion.query(Userlabel).where(Userlabel.name == name).first()
                user = seesion.query(User).where(User.id == int(value)).first()
                if lb and user:
                    seesion.delete(seesion.query(UserlabelLink).where(user_id=user.id, label_id=lb.id))
            elif label == "GraiaGroup":
                lb = seesion.query(Grouplabel).where(Grouplabel.name == name).first()
                group = seesion.query(Group).where(Group.id == int(value)).first()
                if lb and group:
                    seesion.delete(seesion.query(GrouplabelLink).where(group_id=group.id, label_id=lb.id))
            elif label == "GraiaEvent":
                lb = seesion.query(Eventlabel).where(Eventlabel.name == name).first()
                event = seesion.query(Event).where(Event.name == value).first()
                if lb and event:
                    seesion.delete(seesion.query(EventlabelLink).where(event_id=event.id, label_id=lb.id))
            else:
                raise Exception("label error")
            seesion.commit()

    @classmethod
    def create_alice(cls, label: str, name: str, contact: List[str]):
        with Session(cls.engine) as session:
            graia_list = [ModelCore.create_graia(label, name, session) for name in contact]
            cls.create_label(label, name, graia_list, session)
            session.commit()
        return ModelCore.query_label(label, name)

    @classmethod
    def query_graia(cls, label: str):
        with Session(cls.engine) as session:
            if label == "GraiaBot":
                res = session.query(Bot).all()
                return [str(i.id) for i in res]
            elif label == "GraiaGroup":
                res = session.query(Group).all()
                return [str(i.id) for i in res]
            elif label == "GraiaUser":
                res = session.query(User).all()
                return [str(i.id) for i in res]
            elif label == "GraiaEvent":
                res = session.query(Event).all()
                return [str(i.name) for i in res]
            else:
                raise Exception("label is not defined")

    @classmethod
    def query_label(cls, label: str, name: str):
        with Session(cls.engine) as session:
            if label == "GraiaBot":
                return (
                    [str(i.id) for i in res.bots]
                    if (
                        res := session.query(
                            Botlabel,
                        )
                        .where(Botlabel.name == name)
                        .first()
                    )
                    else []
                )

            elif label == "GraiaEvent":
                return (
                    [i.name for i in res.events]
                    if (
                        res := session.query(Eventlabel)
                        .where(Eventlabel.name == name)
                        .first()
                    )
                    else []
                )

            elif label == "GraiaGroup":
                return (
                    [str(i.id) for i in res.groups]
                    if (
                        res := session.query(Grouplabel)
                        .where(Grouplabel.name == name)
                        .first()
                    )
                    else []
                )

            elif label == "GraiaUser":
                return (
                    [str(i.id) for i in res.users]
                    if (
                        res := session.query(Userlabel)
                        .where(Userlabel.name == name)
                        .first()
                    )
                    else []
                )

            else:
                raise Exception("label is not defined")

    @classmethod
    def init_relation(cls, purgo: bool = True):
        with Session(cls.engine) as session:
            if purgo:
                session.query(Botlabel).delete()
                session.query(Grouplabel).delete()
                session.query(Userlabel).delete()
                session.query(Eventlabel).delete()
            session.commit()
            session.flush()
            session.commit()

    @classmethod
    def create_relation(cls, name: str, context: list):
        with Session(cls.engine) as session:
            res = session.query(Relation).where(Relation.name == name).first()
            if res:
                res.contexts = [cls.create_context(i, session) for i in context]
                session.flush()
            else:
                res = Relation(name=name, contexts=[cls.create_context(i, session) for i in context])
                session.add(res)
            session.commit()
            session.refresh(res)
            results = []
            for i in res.contexts:
                result = {
                    'name': i.name,
                    'direction': bool(i.direction),
                    'relationship': ((i.frequency_n, i.frequency_t), i.delayed),
                } | {
                    'bot': session.query(Botlabel)
                    .where(Botlabel.id == i.botlabel_id)
                    .first()
                    .name,
                    'group': session.query(Grouplabel)
                    .where(Grouplabel.id == i.grouplabel_id)
                    .first()
                    .name
                    if i.grouplabel_id
                    else None,
                    'user': session.query(Userlabel)
                    .where(Userlabel.id == i.userlabel_id)
                    .first()
                    .name,
                    'event': session.query(Eventlabel)
                    .where(Eventlabel.id == i.eventlabel_id)
                    .first()
                    .name,
                }

                results.append(result)
            return results

    @classmethod
    def create_context(cls, context: str, session: Session):
        res = session.query(Context).where(Context.name == context.name).first()

        bot = session.query(Botlabel).where(Botlabel.name == context.bot.name).first()
        user = session.query(Userlabel).where(Userlabel.name == context.user.name).first()
        if context.group:
            group = session.query(Grouplabel).where(Grouplabel.name == context.group.name).first()
        else:
            group = None
        event = session.query(Eventlabel).where(Eventlabel.name == context.event.name).first()

        if res:
            res.botlabel_id = bot.id if bot else None
            res.grouplabel_id = group.id if group else None
            res.userlabel_id = user.id if user else None
            res.eventlabel_id = event.id if event else None
            res.frequency_n = context.relationship.frequency[0]
            res.frequency_t = context.relationship.frequency[1]
            res.delayed = context.relationship.delayed
            res.direction = context.direction
            session.flush()
        else:
            res = Context(
                name = context.name,
                botlabel_id = bot.id if bot else None,
                userlabel_id = user.id if user else None,
                grouplabel_id = group.id if group else None,
                eventlabel_id = event.id if event else None,
                frequency_n = context.relationship.frequency[0],
                frequency_t = context.relationship.frequency[1],
                delayed = context.relationship.delayed,
                direction = context.direction,
                )
            session.add(res)

        session.commit()
        return res

    @classmethod
    def query_context(cls, context):
        with Session(cls.engine) as session:
            if (
                res := session.query(Context)
                .where(Context.name == context.name)
                .first()
            ):
                return res
            else:
                return None

    @classmethod
    def query_relation(cls, name: str):
        with Session(cls.engine) as session:
            if res := session.query(Relation).where(Relation.name == name).first():
                return res
            else:
                return None
