EventList = {
	"CONNECTED_TO_SERVER" : 0,

	"ERROR_CONNECTED_TO_ROOM" : 10,
    "CONNECT_TO_ROOM" : 11,
	"CONNECTED_TO_ROOM" : 12,
	"GET_MESSAGE" : 13,
	"KIKCED_FROM_ROOM" : 14,
	"BANED_FROM_ROOM" : 15,
    "ROOM_IS_FULL" : 16,

	"ERROR_CREATED_ROOM" : 20,
    "CREATE_ROOM" : 21,
	"CREATED_ROOM" : 22,
	"SEND_MESSAGE" : 23,
    "SOMEONE_CONNECTED" : 24,
	"SOMEONE_DISCONNECTED" : 25,

	"ERROR_KICK_PLAYER" : 30,
	"KICK_PLAYER" : 31,
	"KICK_PLAYER_SUCСESS" : 32,

	"ERROR_BAN_PLAYER" : 40,
	"BAN_PLAYER" : 41,
	"BAN_PLAYER_SUCCESS" : 42,

    "ROOM_WAS_CLOSED" : 50,
    "INVALID_PASSWORD" : 51,
    "DISCONNECT_ROOM" : 52,
    "DISCONNECTED_FROM_ROOM" : 53
}

def findRoomByKeyWithList(iterable, key, value):
    for index, dict_ in enumerate(iterable):
        if key in dict_ and value in dict_[key]:
            return [True, index]
    return [False, ""]

def findRoomByKey(iterable, key, value):
    for index, dict_ in enumerate(iterable):
        if key in dict_ and dict_[key] == value:
        	return [True, index]
    return [False, ""]

def deleteUserByNickName(owners, rooms, NickName):
	try:
		roomData = findRoomByKeyWithList(rooms, "Users", NickName)
		roomIndex = roomData[1]
		findResult = roomData[0]


		rooms[roomIndex]['Sockets'].pop(rooms[roomIndex]['Users'].index(NickName))
		rooms[roomIndex]['Users'].remove(NickName)
	except TypeError:
		return

def deleteRoomByNickName(owners, rooms, NickName):
	roomData = findRoomByKey(rooms, "OwnerNick", NickName)
	roomIndex = roomData[1]
	findResult = roomData[0]

	for socket in rooms[roomIndex]['Sockets']:
		try:
			socket.send(str(EventList['ROOM_WAS_CLOSED']).encode('cp1251'))
		except ConnectionResetError:
			continue

	rooms.pop(roomIndex)
	owners.remove(NickName)