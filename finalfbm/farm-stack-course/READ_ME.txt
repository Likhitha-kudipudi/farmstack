PROJECT OVERVIEW:
-----------------
---> Multiple Todo Lists
---> Todo Items
---> Real Time Updates 
---> Responsive Design

MONGODB MODEL:
--------------
--->Consists of two main structures
    -> The Todo Lists
    -> The list summary for displaying in the list of all to-do list

fastapi backend will exposed the following restful endpoints so for the to-do list here are the endpoints

->GET/api/lists: Retrieve all todo lists(summary view)
->POST/api/lists:Create a new todo list 
->GET/api/lists/{list_id}: Retrieve a todo list with all items 
->DELETE/api/lists/{list_id}: Delete a specific todo list 


and for todo items here are the endpoints


->POST/api/lists/{list_id}/items: Add a new item to a specific list
->PATCH/api/lists/{list_id}/checked_state: Update checked checked_state
->DELETE/api/lists/{list_id}/items/{item_id}: Delete item from a list

