#importing bson to handle mongodb objects id 
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

#pymango is for return behaviour and update operations
from pymongo import ReturnDocument

#pydantic is for creating data models with validation
from pydantic import BaseModel

#uuid generates uuid's
from uuid import uuid4

#list summary represents the summary of a todo lists
class ListSummary(BaseModel):
    id: str
    name: str
    item_count: int

    @staticmethod
    def from_doc(doc) -> "ListSummary":
        return ListSummary(
            id=str(doc["_id"]),
            name=doc["name"],
            item_count=doc["item_count"],
        )

#todolist items, and a completely todo list which contain both todolist and todolist items
class ToDoListItem(BaseModel):
    id: str
    label: str
    checked: bool

    @staticmethod
    def from_doc(item) -> "ToDoListItem":
        return ToDoListItem(
            id=item["id"],
            label=item["label"],
            checked=item["checked"],
        )

#have a doc static method to create instances from mongodb documents
class ToDoList(BaseModel):
    id: str
    name: str
    items: list[ToDoListItem]

    @staticmethod
    def from_doc(doc) -> "ToDoList":
        return ToDoList(
            id=str(doc["_id"]),
            name=doc["name"],
            items=[ToDoListItem.from_doc(item) for item in doc["items"]],
        )

#this class encapsulates all the database operations
class ToDoDAL:
    def __init__(self, todo_collection: AsyncIOMotorCollection):
        self._todo_collection = todo_collection

    async def list_todo_lists(self, session=None):
        async for doc in self._todo_collection.find(
            {},
            projection={
                "name": 1,
                "item_count": {"$size": "$items"},
            },
            sort={"name": 1},
            session=session,
        ):
            yield ListSummary.from_doc(doc)
        #creates new todo list
    async def create_todo_list(self, name: str, session=None) -> str:
        response = await self._todo_collection.insert_one(
            {"name": name, "items": []},
            session=session,
        )
        return str(response.inserted_id)#returns its id
        #this will retrieve a specific todo list
    async def get_todo_list(self, id: str | ObjectId, session=None) -> ToDoList:
        doc = await self._todo_collection.find_one(
            {"_id": ObjectId(id)},
            session=session,
        )
        return ToDoList.from_doc(doc)

    async def delete_todo_list(self, id: str | ObjectId, session=None) -> bool:
        response = await self._todo_collection.delete_one(
            {"_id": ObjectId(id)},
            session=session,
        )
        return response.deleted_count == 1
        #it will add a specific todolist
    async def create_item(
        self,
        id: str | ObjectId,
        label: str,
        session=None,
    ) -> ToDoList | None:
        result = await self._todo_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {
                "$push": {
                    "items": {
                        "id": uuid4().hex,
                        "label": label,
                        "checked": False,
                    }
                }
            },
            session=session,
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return ToDoList.from_doc(result)
        #it will update the checkstate of a specific item ,which will find the item and updates it
    async def set_checked_state(
        self,
        doc_id: str | ObjectId,
        item_id: str,
        checked_state: bool,
        session=None,
    ) -> ToDoList | None:
        result = await self._todo_collection.find_one_and_update(
            {"_id": ObjectId(doc_id), "items.id": item_id},
            {"$set": {"items.$.checked": checked_state}},
            session=session,
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return ToDoList.from_doc(result)
        #deletes item
    async def delete_item(
        self,
        doc_id: str | ObjectId,
        item_id: str,
        session=None,
    ) -> ToDoList | None:
        result = await self._todo_collection.find_one_and_update(
            {"_id": ObjectId(doc_id)},
            {"$pull": {"items": {"id": item_id}}},
            session=session,
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return ToDoList.from_doc(result)
#the key points of this file ,is that all methods are asynchronous using the asyn await syntax for
# non blocking databases operations and theres also extensive use of type hints for better code clarity
#and ide support