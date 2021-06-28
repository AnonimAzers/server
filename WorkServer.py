import socket
import threading
import time
import ServerFunctions as ServFunc
from ServerFunctions import EventList

connections = []
owners = []
rooms = []

def listenMsg(index):
    NickName = ""
    Socket = connections[index]
    while True:
        try:
            text = Socket.recv(257)
        except ConnectionResetError:
            connections.remove(Socket)
            if NickName != "":
                if NickName in owners:
                    ServFunc.deleteRoomByNickName(owners,rooms,NickName)
                else:
                    RoomData = ServFunc.findRoomByKeyWithList(rooms, "Users", NickName)
                    roomIndex = roomData[0]
                    findResult = roomData[1]
                    if findResult:
                        ServFunc.deleteRoomByNickName(owners, rooms, NickName)
                        try:
                            rooms[roomIndex]['OwnerSocket'].send(str(("{} {}".format(EventList["SOMEONE_DISCONNECTED"], NickName))).encode('cp1251'))
                        except ConnectionResetError:
                            ServFunc.deleteRoomByNickName(owners, rooms, rooms[roomIndex]['OwnerNick'])
                        except IndexError:
                            break

            break

        data = text.decode('cp1251')

        try:
            text_data = {x[0]:x[1] for x in [y.split("=") for y in data.split(";") if len(y)]}
        except IndexError:
            continue

        try:
            print(text_data)
            NickName = text_data['NickName']
            text_data['Code'] = int(text_data['Code'])
        except KeyError:
            continue



#################################CREATE_ROOM############################################################################
        if text_data['Code'] == EventList["CREATE_ROOM"]:
            if ServFunc.findRoomByKey(rooms, "RoomId", int(text_data['RoomId']))[0] == False:
                try:
                    Socket.send(str(EventList["CREATED_ROOM"]).encode('cp1251'))
                except ConnectionResetError:
                    break
                rooms.append({
    				'OwnerNick' : NickName,
    				'OwnerSocket' : Socket,
                    'RoomId' : int(text_data['RoomId']),
                    'Password' : text_data['Password'],
                    'Users' : [],
                    'Sockets' : [],
                    'Banned' : []
                    })

                owners.append(NickName)
            else:
                try:
                    Socket.send(str(EventList["ERROR_CREATED_ROOM"]).encode('cp1251'))
                except ConnectionResetError:
                    break



#################################CONNECT_TO_ROOM########################################################################
        if text_data['Code'] == EventList["CONNECT_TO_ROOM"]:
            roomData = ServFunc.findRoomByKey(rooms, "RoomId", int(text_data['RoomId']))
            roomIndex = roomData[1]
            findResult = roomData[0]

            if findResult != False:
                if NickName in rooms[roomIndex]['Banned']:
                    try:
                        Socket.send(str(EventList["BANED_FROM_ROOM"]).encode('cp1251'))
                        continue
                    except ConnectionResetError:
                        break


                if len(rooms[roomIndex]['Users']) < 17:
                    if text_data['Password'] == rooms[roomIndex]['Password']:

                        try:
                            Socket.send(str(EventList["CONNECTED_TO_ROOM"]).encode('cp1251'))
                        except ConnectionResetError:
                            break

                        try:
                            rooms[roomIndex]['OwnerSocket'].send(str(("{} {}".format(EventList["SOMEONE_CONNECTED"], NickName))).encode('cp1251'))
                        except ConnectionResetError:
                            ServFunc.deleteRoomByNickName(owners, rooms, rooms[roomIndex]['OwnerNick'])
                            break

                        rooms[roomIndex]['Users'].append(NickName)
                        rooms[roomIndex]['Sockets'].append(Socket)
                    else:
                        try:
                            Socket.send(str(EventList["INVALID_PASSWORD"]).encode('cp1251'))
                        except ConnectionResetError:
                            break
                else:
                    try:
                        Socket.send(str(EventList["ROOM_IS_FULL"]).encode('cp1251'))
                    except ConnectionResetError:
                        break
            else:
                try:
                    Socket.send(str(EventList["ERROR_CONNECTED_TO_ROOM"]).encode('cp1251'))
                except ConnectionResetError:
                    break


#################################SEND_MESSAGE##########################################################################
        if text_data['Code'] == EventList["SEND_MESSAGE"]:
            roomData = ServFunc.findRoomByKey(rooms, "RoomId", int(text_data['RoomId']))
            roomIndex = roomData[1]
            findResult = roomData[0]
            for index, sock in enumerate(rooms[roomIndex]['Sockets']):
                try:
                    sock.send(("{} {}".format(EventList["GET_MESSAGE"], text_data["Text"])).encode('cp1251'))
                except ConnectionResetError:
                    ServFunc.deleteUserByNickName(owners, rooms, rooms[roomIndex]['Users'][index])




#################################DISCONNECT_ROOM########################################################################
        if text_data['Code'] == EventList["DISCONNECT_ROOM"]:
            roomData = ServFunc.findRoomByKey(rooms, "RoomId", int(text_data['RoomId']))
            roomIndex = roomData[1]
            findResult = roomData[0]

            if NickName == rooms[roomIndex]['OwnerNick']:
                ServFunc.deleteRoomByNickName(owners, rooms, NickName)
            else:
                ServFunc.deleteUserByNickName(owners, rooms, NickName)
                try:
                    rooms[roomIndex]['OwnerSocket'].send(str(("{} {}".format(EventList["SOMEONE_DISCONNECTED"], NickName))).encode('cp1251'))
                except ConnectionResetError:
                    ServFunc.deleteRoomByNickName(owners, rooms, rooms[roomIndex]['OwnerNick'])
                    continue

            try:
                Socket.send(str(EventList["DISCONNECTED_FROM_ROOM"]).encode('cp1251'))
            except ConnectionResetError:
                break



#################################KICK_PLAYER############################################################################
        if text_data['Code'] == EventList["KICK_PLAYER"]:
            roomData = ServFunc.findRoomByKey(rooms, "RoomId", int(text_data['RoomId']))
            roomIndex = roomData[1]
            findResult = roomData[0]
            if text_data['Kick'] in rooms[roomIndex]['Users']:
                UserIndex = rooms[roomIndex]['Users'].index(text_data['Kick'])

                try:
                    rooms[roomIndex]['Sockets'][UserIndex].send(str(EventList['KIKCED_FROM_ROOM']).encode('cp1251'))
                except ConnectionResetError:
                    ServFunc.deleteUserByNickName(owners, rooms, rooms[roomIndex]['Users'][UserIndex])
                    continue

                ServFunc.deleteUserByNickName(owners, rooms, rooms[roomIndex]['Users'][UserIndex])

                try:
                    Socket.send(("{} {}".format(EventList["KICK_PLAYER_SUCСESS"], text_data['Kick'])).encode('cp1251'))
                except ConnectionResetError:
                    ServFunc.deleteRoomByNickName(owners, rooms, NickName)
                    break

            else:
                try:
                    Socket.send(str(EventList["ERROR_KICK_PLAYER"]).encode('cp1251'))
                except ConnectionResetError:
                    ServFunc.deleteRoomByNickName(owners, rooms, NickName)
                    break




#################################BAN_PLAYER#############################################################################
        if text_data['Code'] == EventList["BAN_PLAYER"]:
            roomData = ServFunc.findRoomByKey(rooms, "RoomId", int(text_data['RoomId']))
            roomIndex = roomData[1]
            findResult = roomData[0]
            if text_data['Ban'] in rooms[roomIndex]['Users']:
                UserIndex = rooms[roomIndex]['Users'].index(text_data['Ban'])

                try:
                    rooms[roomIndex]['Sockets'][UserIndex].send(str(EventList['BANED_FROM_ROOM']).encode('cp1251'))
                except ConnectionResetError:
                    ServFunc.deleteUserByNickName(owners, rooms, rooms[roomIndex]['Users'][UserIndex])
                    rooms[roomIndex]['Banned'].append(text_data['Ban'])
                    continue

                ServFunc.deleteUserByNickName(owners, rooms, rooms[roomIndex]['Users'][UserIndex])
                rooms[roomIndex]['Banned'].append(text_data['Ban'])


                try:
                    Socket.send(("{} {}".format(EventList["BAN_PLAYER_SUCCESS"], text_data['Ban'])).encode('cp1251'))
                except ConnectionResetError:
                    ServFunc.deleteRoomByNickName(owners, rooms, NickName)
                    break
            else:
                try:
                    Socket.send(str(EventList["ERROR_BAN_PLAYER"]).encode('cp1251'))
                except ConnectionResetError:
                    ServFunc.deleteRoomByNickName(owners, rooms, NickName)
                    break


sock = socket.socket()
sock.bind(('', 3253))
sock.listen()

while True:
    conn, addr = sock.accept()
    connections.append(conn)
    thread = threading.Thread(target = listenMsg, args = (len(connections)-1, ))
    thread.start()
