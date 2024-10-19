| Old endpoint                  | Old methods   | New endpoint                                                                 | Description                                               |
|-------------------------------|---------------|------------------------------------------------------------------------------|-----------------------------------------------------------|
|                               |               | /api/                                                                        | Swagger page
| /users                        | GET           | [deleted]                                                                    | 
| /races                        | GET           | [deleted]                                                                    | 
| /homepage                     |               | [deleted]                                                                    | 
| /testpage                     |               | [deleted]                                                                    | 
|                               |               |                                                                              | 
| /api/user                     | POST          | /api/user                                                                    | Get all users
|                               |               | /api/user/<uuid:id>                                                          | Get user based on id
|                               |               | /api/user/<str:name>                                                         | Get user based on name
| /api/register                 | POST          | /api/account/register                                                        | Register account
| /api/login                    | POST          | /api/account/login                                                           | Login
| /api/logout                   | POST          | /api/account/logout                                                          | Logout
| /api/coordinates_list         |               | /api/planet/buy_list                                                         | Get list of buy options    
|                               | GET           | /api/planet                                                                  | Get all planets
|                               |               | /api/planet/<uuid:id>                                                        | Get planet by id
|                               |               | /api/planet/<int:x><int:y>                                                   | Get planet by (x, y)
| /api/planet                   | GET, POST     | /api/planet/add                                                              | Add new planet
| /api/settlement               | GET, POST     | /api/settlement                                                              | Get all settlements
|                               |               | /api/settlement/<uuid:id>                                                    | Get settlement by id
|                               |               | /api/settlement/<uuid:planet><int:number>                                    | Get settlement by planet id and number
| /api/add_building             | GET, POST     | /api/building                                                                | Get all buildings
|                               |               | /api/building/<uuid:id>                                                      | Get building by id
|                               |               | /api/building/<uuid:settlement><int:x><int:y>                                | Get building by id
|                               |               | /api/building/add                                                            | Add new building
| /api/remove_building          | POST          | /api/building/delete                                                         | Delete building
| /api/upgrade_building         | GET, POST     | /api/building/upgrade                                                        | Upgrade building
| /api/get_resources            | GET           | /api/planet/resources                                                        | Get planet resources
| /api/get_building_level       | GET           | /api/building/<uuid:id>/level                                                | Get building level by id
|                               |               | /api/building/level/<uuid:settlement><int:x><int:y>                          | Get building level by settlement id and (x, y)
|                               |               | /api/building/level/<int:planet><int:settlement><int:x><int:y>               | Get building level by settlement id and (x, y)
| /api/race_members             | GET           | /api/race/members/<uuid:id>                                                  | Get all race members
| /api/race                     | GET, POST     | /api/race                                                                    | Get list of all (race_id, race_name) pairs
|                               |               | /api/race/<str:name>                                                         | Get race by name
|                               |               | /api/race/<uuid:id>                                                          | Get race by name
|                               |               | /api/race/create                                                             | Create new race
| /api/join_race                | GET, POST     | /api/race/join                                                               | Join existing race
| /api/leave_race               | POST          | /api/race/leave                                                              | Leave race
| /api/add_unit                 | POST          | /api/unit/add_unit                                                           | 
| /api/get_units_in_training    | GET           | /api/building/barrack/training                                               | 
| /api/get_construction_time    | GET           | /api/building/construction_time                                              | 
| /api/get_unit_training_time   | GET           | /api/unit/training_time                                                      | 
| /api/get_barrack_space        | GET           | /api/building/barrack/space                                                  | 
| /api/start_farming            | POST          | /api/building/start_farming                                                  | 
| /api/collect_resources        | POST          | /api/building/collect                                                        | 
| /api/get_all_planets          | POST          | x                                                                            | 
| /api/<path:endpoint>          |               | x                                                                            | 
