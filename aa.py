from memory import *
from entity import *
from local import *
from gui import *
from helper import *
from convar import *
from overlay import *
import platform
import math
from ctypes import *
import subprocess
import requests
import time
import sys
import os
ntdll = windll.ntdll
k32 = windll.kernel32
u32 = windll.user32


hwid = str(str(subprocess.check_output('wmic csproduct get uuid')).strip().replace(r"\r", "").split(r"\n")[1].strip())
r = requests.get("https://cdn.myuuiii.com/avilon/hwid.txt")

def printSlow(text):
    for char in text:
        print(char, end="")
        sys.stdout.flush()
        time.sleep(.1)

def hwidcheck():
    if hwid in r.text:
        printSlow("Access granted...")
        print('')
        time.sleep(.1)
    else:
        print("Error! HWID Not I Database!")
        print("Please contact (yuui#0766) for help. HWID: " + hwid)
        os.system('pause >NUL')

    ##hwidcheck()

#
# Laplus@2023
#

stdalone_rcs = True
aim_rcs = True

aim = True
aim_head = True
aim_key = 107
aim_smooth = 8
aim_fov = 7 / 180.0

trigger_key = 111
magnetic_fov = 4 /180.0
magnetic_smooth = 2

g_old_punch = 0
g_previous_tick = 0
g_current_tick = 0
g_exit_key = 92
  

class Vector3(Structure):
    _fields_ = [('x', c_float), ('y', c_float), ('z', c_float)]


class PROCESSENTRY32(Structure):
    _fields_ = [
        ("dwSize", c_uint32),
        ("cntUsage", c_uint32),
        ("th32ProcessID", c_uint32),
        ("th32DefaultHeapID", c_uint64),
        ("th32ModuleID", c_uint32),
        ("cntThreads", c_uint32),
        ("th32ParentProcessID", c_uint32),
        ("pcPriClassBase", c_uint32),
        ("dwFlags", c_uint32),
        ("szExeFile", c_char * 260)
    ]


class Process:
    @staticmethod
    def get_process_handle(name):
        handle = 0
        entry = PROCESSENTRY32()
        snap = k32.CreateToolhelp32Snapshot(0x00000002, 0)
        entry.dwSize = sizeof(PROCESSENTRY32)
        while k32.Process32Next(snap, pointer(entry)):
            if entry.szExeFile == name.encode("ascii", "ignore"):
                handle = k32.OpenProcess(0x430, 0, entry.th32ProcessID)
                break
        k32.CloseHandle(snap)
        return handle

    @staticmethod
    def get_process_peb(handle, wow64):
        buffer = (c_uint64 * 6)(0)
        if wow64:
            if ntdll.NtQueryInformationProcess(handle, 26, pointer(buffer), 8, 0) == 0:
                return buffer[0]
        else:
            if ntdll.NtQueryInformationProcess(handle, 0, pointer(buffer), 48, 0) == 0:
                return buffer[1]
        return 0

    def __init__(self, name):
        self.mem2 = self.get_process_handle(name)
        if self.mem2 == 0:
            raise Exception("Process [" + name + "] not found!")
        self.peb = self.get_process_peb(self.mem2, True)
        if self.peb == 0:
            self.peb = self.get_process_peb(self.mem2, False)
            self.wow64 = False
        else:
            self.wow64 = True

    def is_running(self):
        buffer = c_uint32()
        k32.GetExitCodeProcess(self.mem2, pointer(buffer))
        return buffer.value == 0x103

    def read_vec3(self, address):
        buffer = Vector3()
        ntdll.NtReadVirtualMemory(self.mem2, c_long(address), pointer(buffer), 12, 0)
        return buffer

    def read_buffer(self, address, length):
        buffer = (c_uint8 * length)()
        ntdll.NtReadVirtualMemory(self.mem2, address, buffer, length, 0)
        return buffer

    def read_string(self, address, length=120):
        buffer = create_string_buffer(length)
        ntdll.NtReadVirtualMemory(self.mem2, address, buffer, length, 0)
        return buffer.value

    def read_unicode(self, address, length=120):
        buffer = create_unicode_buffer(length)
        ntdll.NtReadVirtualMemory(self.mem2, address, pointer(buffer), length, 0)
        return buffer.value

    def read_float(self, address, length=4):
        buffer = c_float()
        ntdll.NtReadVirtualMemory(self.mem2, c_long(address), pointer(buffer), length, 0)
        return buffer.value

    def read_i8(self, address, length=1):
        buffer = c_uint8()
        ntdll.NtReadVirtualMemory(self.mem2, address, pointer(buffer), length, 0)
        return buffer.value

    def read_i16(self, address, length=2):
        buffer = c_uint16()
        ntdll.NtReadVirtualMemory(self.mem2, address, pointer(buffer), length, 0)
        return buffer.value

    def read_i32(self, address, length=4):
        buffer = c_uint32()
        ntdll.NtReadVirtualMemory(self.mem2, address, pointer(buffer), length, 0)
        return buffer.value

    def read_i64(self, address, length=8):
        buffer = c_uint64()
        ntdll.NtReadVirtualMemory(self.mem2, c_uint64(address), pointer(buffer), length, 0)
        return buffer.value

    def write_float(self, address, value):
        buffer = c_float(value)
        return ntdll.NtWriteVirtualMemory(self.mem2, address, pointer(buffer), 4, 0) == 0

    def write_i8(self, address, value):
        buffer = c_uint8(value)
        return ntdll.NtWriteVirtualMemory(self.mem2, address, pointer(buffer), 1, 0) == 0

    def write_i16(self, address, value):
        buffer = c_uint16(value)
        return ntdll.NtWriteVirtualMemory(self.mem2, address, pointer(buffer), 2, 0) == 0

    def write_i64(self, address, value):
        buffer = c_uint64(value)
        return ntdll.NtWriteVirtualMemory(self.mem2, address, pointer(buffer), 8, 0) == 0

    def get_module(self, name):
        if self.wow64:
            a0 = [0x04, 0x0C, 0x14, 0x28, 0x10]
        else:
            a0 = [0x08, 0x18, 0x20, 0x50, 0x20]
        a1 = self.read_i64(self.read_i64(self.peb + a0[1], a0[0]) + a0[2], a0[0])
        a2 = self.read_i64(a1 + a0[0], a0[0])
        while a1 != a2:
            val = self.read_unicode(self.read_i64(a1 + a0[3], a0[0]))
            if str(val).lower() == name.lower():
                return self.read_i64(a1 + a0[4], a0[0])
            a1 = self.read_i64(a1, a0[0])
        raise Exception("Module [" + name + "] not found!")

    def get_export(self, module, name):
        if module == 0:
            return 0
        a0 = self.read_i32(module + self.read_i16(module + 0x3C) + (0x88 - self.wow64 * 0x10)) + module
        a1 = [self.read_i32(a0 + 0x18), self.read_i32(a0 + 0x1c), self.read_i32(a0 + 0x20), self.read_i32(a0 + 0x24)]
        while a1[0] > 0:
            a1[0] -= 1
            export_name = self.read_string(module + self.read_i32(module + a1[2] + (a1[0] * 4)), 120)
            if name.encode('ascii', 'ignore') == export_name:
                a2 = self.read_i16(module + a1[3] + (a1[0] * 2))
                a3 = self.read_i32(module + a1[1] + (a2 * 4))
                return module + a3
        raise Exception("Export [" + name + "] not found!")

    def find_pattern(self, module_name, pattern, mask):
        a0 = self.get_module(module_name)
        a1 = self.read_i32(a0 + 0x03C) + a0
        a2 = self.read_i32(a1 + 0x01C)
        a3 = self.read_i32(a1 + 0x02C)
        a4 = self.read_buffer(a0 + a3, a2)
        for a5 in range(0, a2):
            a6 = 0
            for a7 in range(0, pattern.__len__()):
                if mask[a7] == 'x' and a4[a5 + a7] != pattern[a7]:
                    break
                a6 = a6 + 1
            if a6 == pattern.__len__():
                return a0 + a3 + a5
        return 0


class VirtualTable:
    def __init__(self, table):
        self.table = table

    def function(self, index):
        return mem2.read_i32(mem2.read_i32(self.table) + index * 4)


class InterfaceTable:
    def __init__(self, name):
        self.table_list = mem2.read_i32(mem2.read_i32(mem2.get_export(mem2.get_module(name), 'CreateInterface') - 0x6A))

    def get_interface(self, name):
        a0 = self.table_list
        while a0 != 0:
            if name.encode('ascii', 'ignore') == mem2.read_string(mem2.read_i32(a0 + 0x4), 120)[0:-3]:
                return VirtualTable(mem2.read_i32(mem2.read_i32(a0) + 1))
            a0 = mem2.read_i32(a0 + 0x8)
        raise Exception("Interface [" + name + "] not found!")


class NetVarTable:
    def __init__(self, name):
        self.table = 0
        a0 = mem2.read_i32(mem2.read_i32(vt.client.function(8) + 1))
        while a0 != 0:
            a1 = mem2.read_i32(a0 + 0x0C)
            if name.encode('ascii', 'ignore') == mem2.read_string(mem2.read_i32(a1 + 0x0C), 120):
                self.table = a1
                return
            a0 = mem2.read_i32(a0 + 0x10)
        raise Exception("NetVarTable [" + name + "] not found!")

    def get_offset(self, name):
        offset = self.__get_offset(self.table, name)
        if offset == 0:
            raise Exception("Offset [" + name + "] not found!")
        return offset

    def __get_offset(self, address, name):
        a0 = 0
        for a1 in range(0, mem2.read_i32(address + 0x4)):
            a2 = a1 * 60 + mem2.read_i32(address)
            a3 = mem2.read_i32(a2 + 0x2C)
            a4 = mem2.read_i32(a2 + 0x28)
            if a4 != 0 and mem2.read_i32(a4 + 0x4) != 0:
                a5 = self.__get_offset(a4, name)
                if a5 != 0:
                    a0 += a3 + a5
            if name.encode('ascii', 'ignore') == mem2.read_string(mem2.read_i32(a2), 120):
                return a3 + a0
        return a0


class ConVar:
    def __init__(self, name):
        self.address = 0
        a0 = mem2.read_i32(mem2.read_i32(mem2.read_i32(vt.cvar.table + 0x34)) + 0x4)
        while a0 != 0:
            if name.encode('ascii', 'ignore') == mem2.read_string(mem2.read_i32(a0 + 0x0C)):
                self.address = a0
                return
            a0 = mem2.read_i32(a0 + 0x4)
        raise Exception("ConVar [" + name + "] not found!")

    def get_int(self):
        a0 = c_int32()
        a1 = mem2.read_i32(self.address + 0x30) ^ self.address
        ntdll.memcpy(pointer(a0), pointer(c_int32(a1)), 4)
        return a0.value

    def get_float(self):
        a0 = c_float()
        a1 = mem2.read_i32(self.address + 0x2C) ^ self.address
        ntdll.memcpy(pointer(a0), pointer(c_int32(a1)), 4)
        return a0.value


class InterfaceList:
    def __init__(self):
        table = InterfaceTable('client.dll')
        self.client = table.get_interface('VClient')
        self.entity = table.get_interface('VClientEntityList')
        table = InterfaceTable('engine.dll')
        self.engine = table.get_interface('VEngineClient')
        table = InterfaceTable('vstdlib.dll')
        self.cvar = table.get_interface('VEngineCvar')
        table = InterfaceTable('inputsystem.dll')
        self.input = table.get_interface('InputSystemVersion')


class NetVarList:
    def __init__(self):
        table = NetVarTable('DT_BasePlayer')
        self.m_iHealth = table.get_offset('m_iHealth')
        self.m_vecViewOffset = table.get_offset('m_vecViewOffset[0]')
        self.m_lifeState = table.get_offset('m_lifeState')
        self.m_nTickBase = table.get_offset('m_nTickBase')
        
        self.m_vecPunch = table.get_offset('m_Local') + 0x70

        table = NetVarTable('DT_BaseEntity')
        self.m_iTeamNum = table.get_offset('m_iTeamNum')
        
        self.m_vecOrigin = table.get_offset('m_vecOrigin')

        table = NetVarTable('DT_CSPlayer')
        self.m_hActiveWeapon = table.get_offset('m_hActiveWeapon')
        self.m_iShotsFired = table.get_offset('m_iShotsFired')
        
        self.m_iCrossHairID = table.get_offset('m_bHasDefuser') + 0x5C
        self.m_iGlowIndex = table.get_offset('m_flFlashDuration') + 0x18

        table = NetVarTable('DT_BaseAnimating')
        self.m_dwBoneMatrix = table.get_offset('m_nForceBone') + 0x1C

        table = NetVarTable('DT_BaseAttributableItem')
        self.m_iItemDefinitionIndex = table.get_offset('m_iItemDefinitionIndex')

        self.dwEntityList = vt.entity.table - (mem2.read_i32(vt.entity.function(6) + 0x22) - 0x38)
        self.dwClientState = mem2.read_i32(mem2.read_i32(vt.engine.function(18) + 0x21))
        self.dwGetLocalPlayer = mem2.read_i32(vt.engine.function(12) + 0x16)
        self.dwViewAngles = mem2.read_i32(vt.engine.function(19) + 0x191)
        self.dwMaxClients = mem2.read_i32(vt.engine.function(20) + 0x07)
        self.dwState = mem2.read_i32(vt.engine.function(26) + 0x07)
        self.dwButton = mem2.read_i32(vt.input.function(28) + 0xC1 + 2)


class Player:
    def __init__(self, address):
        self.address = address
        
    def get_team_num(self):
        return mem2.read_i32(self.address + nv.m_iTeamNum)

    def get_health(self):
        return mem2.read_i32(self.address + nv.m_iHealth)

    def get_life_state(self):
        return mem2.read_i32(self.address + nv.m_lifeState)

    def get_tick_count(self):
        return mem2.read_i32(self.address + nv.m_nTickBase)

    def get_shots_fired(self):
        return mem2.read_i32(self.address + nv.m_iShotsFired)

    def get_cross_index(self):
        return mem2.read_i32(self.address + nv.m_iCrossHairID)

    def get_weapon(self):
        a0 = mem2.read_i32(self.address + nv.m_hActiveWeapon)
        return mem2.read_i32(nv.dwEntityList + ((a0 & 0xFFF) - 1) * 0x10)

    def get_weapon_id(self):
        return mem2.read_i32(self.get_weapon() + nv.m_iItemDefinitionIndex)

    def get_origin(self):
        return mem2.read_vec3(self.address + nv.m_vecOrigin)

    def get_vec_view(self):
        return mem2.read_vec3(self.address + nv.m_vecViewOffset)

    def get_eye_pos(self):
        v = self.get_vec_view()
        o = self.get_origin()
        return Vector3(v.x + o.x, v.y + o.y, v.z + o.z)

    def get_vec_punch(self):
        return mem2.read_vec3(self.address + nv.m_vecPunch)

    def get_bone_pos(self, index):
        a0 = 0x30 * index
        a1 = mem2.read_i32(self.address + nv.m_dwBoneMatrix)
        return Vector3(
            mem2.read_float(a1 + a0 + 0x0C),
            mem2.read_float(a1 + a0 + 0x1C),
            mem2.read_float(a1 + a0 + 0x2C)
        )

    def is_valid(self):
        health = self.get_health()
        return self.address != 0 and self.get_life_state() == 0 and 0 < health < 1338


class Engine:
    @staticmethod
    def get_local_player():
        return mem2.read_i32(nv.dwClientState + nv.dwGetLocalPlayer)

    @staticmethod
    def get_view_angles():
        return mem2.read_vec3(nv.dwClientState + nv.dwViewAngles)

    @staticmethod
    def get_max_clients():
        return mem2.read_i32(nv.dwClientState + nv.dwMaxClients)

    @staticmethod
    def is_in_game():
        return mem2.read_i8(nv.dwClientState + nv.dwState) >> 2


class Entity:
    @staticmethod
    def get_client_entity(index):
        return Player(mem2.read_i32(nv.dwEntityList + index * 0x10))


class InputSystem:
    @staticmethod
    def is_button_down(button):
        a0 = mem2.read_i32(vt.input.table + ((button >> 5) * 4) + nv.dwButton)
        return (a0 >> (button & 31)) & 1


class Math:
    @staticmethod
    def sin_cos(radians):
        return [math.sin(radians), math.cos(radians)]

    @staticmethod
    def rad2deg(x):
        return x * 3.141592654

    @staticmethod
    def deg2rad(x):
        return x * 0.017453293

    @staticmethod
    def angle_vec(angles):
        s = Math.sin_cos(Math.deg2rad(angles.x))
        y = Math.sin_cos(Math.deg2rad(angles.y))
        return Vector3(s[1] * y[1], s[1] * y[0], -s[0])

    @staticmethod
    def vec_normalize(vec):
        radius = 1.0 / (math.sqrt(vec.x * vec.x + vec.y * vec.y + vec.z * vec.z) + 1.192092896e-07)
        vec.x *= radius
        vec.y *= radius
        vec.z *= radius
        return vec

    @staticmethod
    def vec_angles(forward):
        if forward.y == 0.00 and forward.x == 0.00:
            yaw = 0
            pitch = 270.0 if forward.z > 0.00 else 90.0
        else:
            yaw = math.atan2(forward.y, forward.x) * 57.295779513
            if yaw < 0.00:
                yaw += 360.0
            tmp = math.sqrt(forward.x * forward.x + forward.y * forward.y)
            pitch = math.atan2(-forward.z, tmp) * 57.295779513
            if pitch < 0.00:
                pitch += 360.0
        return Vector3(pitch, yaw, 0.00)

    @staticmethod
    def vec_clamp(v):
        if 89.0 < v.x <= 180.0:
            v.x = 89.0
        if v.x > 180.0:
            v.x -= 360.0
        if v.x < -89.0:
            v.x = -89.0
        v.y = math.fmod(v.y + 180.0, 360.0) - 180.0
        v.z = 0.00
        return v

    @staticmethod
    def vec_dot(v0, v1):
        return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

    @staticmethod
    def vec_length(v):
        return v.x * v.x + v.y * v.y + v.z * v.z

    @staticmethod
    def get_fov(va, angle):
        a0 = Math.angle_vec(va)
        a1 = Math.angle_vec(angle)
        return Math.rad2deg(math.acos(Math.vec_dot(a0, a1) / Math.vec_length(a0)))

def get_target_angle(local_p, target, bone_id):
    m = target.get_bone_pos(bone_id)
    c = local_p.get_eye_pos()
    c.x = m.x - c.x
    c.y = m.y - c.y
    c.z = m.z - c.z
    c = Math.vec_angles(Math.vec_normalize(c))
    if InputSystem.is_button_down(aim_key) and aim_rcs and local_p.get_shots_fired() > 1:
        p = local_p.get_vec_punch()
        c.x -= p.x * 2.0
        c.y -= p.y * 2.0
        c.z -= p.z * 2.0
    return Math.vec_clamp(c)


_target = Player(0)
_target_bone = 0
_bones = [6, 7, 8]


def target_set(target):
    global _target
    _target = target


def get_best_target(va, local_p):
    global _target_bone
    a0 = 9999.9
    for i in range(1, Engine.get_max_clients()):
        entity = Entity.get_client_entity(i)
        if not entity.is_valid():
            continue
        if not mp_teammates_are_enemies.get_int() and local_p.get_team_num() == entity.get_team_num():
            continue
        if aim_head:
            fov = Math.get_fov(va, get_target_angle(local_p, entity, 8))
            if fov < a0:
                a0 = fov
                target_set(entity)
                _target_bone = 8
        else:
            for j in range(0, _bones.__len__()):
                fov = Math.get_fov(va, get_target_angle(local_p, entity, _bones[j]))
                if fov < a0:
                    a0 = fov
                    target_set(entity)
                    _target_bone = _bones[j]
    return a0 != 9999

def aim_at_closetarget(sensitivity, va, angle):
    global g_current_tick
    global g_previous_tick
    y = va.x - angle.x
    x = va.y - angle.y
    if y > 89.0:
        y = 89.0
    elif y < -89.0:
        y = -89.0
    if x > 180.0:
        x -= 360.0
    elif x < -180.0:
        x += 360.0
    if math.fabs(x) / 180.0 >= magnetic_fov:
        target_set(Player(0))
        return
    if math.fabs(y) / 89.0 >= magnetic_fov:
        target_set(Player(0))
        return
    x = (x / sensitivity) / 0.022
    y = (y / sensitivity) / -0.022
    if aim_smooth > 1.00:
        sx = 0.00
        sy = 0.00
        if sx < x:
            sx += 1.0 + (x / aim_smooth)
        elif sx > x:
            sx -= 1.0 - (x / aim_smooth)
        if sy < y:
            sy += 1.0 + (y / aim_smooth)
        elif sy > y:
            sy -= 1.0 - (y / aim_smooth)
    else:
        sx = x
        sy = y
    if g_current_tick - g_previous_tick > 0:
        g_previous_tick = g_current_tick
        u32.mouse_event(0x0001, int(sx), int(sy), 0, 0)

def aim_at_target(sensitivity, va, angle):
    global g_current_tick
    global g_previous_tick
    y = va.x - angle.x
    x = va.y - angle.y
    if y > 89.0:
        y = 89.0
    elif y < -89.0:
        y = -89.0
    if x > 180.0:
        x -= 360.0
    elif x < -180.0:
        x += 360.0
    if math.fabs(x) / 180.0 >= aim_fov:
        target_set(Player(0))
        return
    if math.fabs(y) / 89.0 >= aim_fov:
        target_set(Player(0))
        return
    x = (x / sensitivity) / 0.022
    y = (y / sensitivity) / -0.022
    if aim_smooth > 1.00:
        sx = 0.00
        sy = 0.00
        if sx < x:
            sx += 1.0 + (x / aim_smooth)
        elif sx > x:
            sx -= 1.0 - (x / aim_smooth)
        if sy < y:
            sy += 1.0 + (y / aim_smooth)
        elif sy > y:
            sy -= 1.0 - (y / aim_smooth)
    else:
        sx = x
        sy = y
    if g_current_tick - g_previous_tick > 0:
        g_previous_tick = g_current_tick
        u32.mouse_event(0x0001, int(sx), int(sy), 0, 0)

#extra recode


#end of extra
        

if __name__ == "__main__":
    if platform.architecture()[0] != '64bit':
        print('[!]64bit python required')
        exit(0)
    try:
        mem2 = Process('csgo.exe')

        vt = InterfaceList()
        nv = NetVarList()
        _sensitivity = ConVar('sensitivity')
        mp_teammates_are_enemies = ConVar('mp_teammates_are_enemies')

    
    except Exception as e:
        print(e)
        exit(0)

    
        
    print('[*]VirtualTablesCheck')
    print('    VClient:            ' + hex(vt.client.table))
    print('    VClientEntityList:  ' + hex(vt.entity.table))
    print('    VEngineClient:      ' + hex(vt.engine.table))
    print('    VEngineCvar:        ' + hex(vt.cvar.table))
    print('    InputSystemVersion: ' + hex(vt.input.table))
    print('[*]OffsetsCheck')
    print('    EntityList:         ' + hex(nv.dwEntityList))
    print('    ClientState:        ' + hex(nv.dwClientState))
    print('    GetLocalPlayer:     ' + hex(nv.dwGetLocalPlayer))
    print('    GetViewAngles:      ' + hex(nv.dwViewAngles))
    print('    GetMaxClients:      ' + hex(nv.dwMaxClients))
    print('    IsInGame:           ' + hex(nv.dwState))
    print('[*]NetVarsCheck')
    print('    m_iHealth:          ' + hex(nv.m_iHealth))
    print('    m_vecViewOffset:    ' + hex(nv.m_vecViewOffset))
    print('    m_lifeState:        ' + hex(nv.m_lifeState))
    print('    m_nTickBase:        ' + hex(nv.m_nTickBase))
    print('    m_vecPunch:         ' + hex(nv.m_vecPunch))
    print('    m_iTeamNum:         ' + hex(nv.m_iTeamNum))
    print('    m_vecOrigin:        ' + hex(nv.m_vecOrigin))
    print('    m_hActiveWeapon:    ' + hex(nv.m_hActiveWeapon))
    print('    m_iShotsFired:      ' + hex(nv.m_iShotsFired))
    print('    m_iCrossHairID:     ' + hex(nv.m_iCrossHairID))
    print('    m_dwBoneMatrix:     ' + hex(nv.m_dwBoneMatrix))

    print('[*]Info')
    print('    Creator:            Laplus :3 (i love cock)')
    
##

##

        

            
    while mem2.is_running() and not InputSystem.is_button_down(g_exit_key):
        k32.Sleep(1)
        if Engine.is_in_game():
            try:
                self = Entity.get_client_entity(Engine.get_local_player())
                fl_sensitivity = _sensitivity.get_float()
                view_angle = Engine.get_view_angles()
                
                if InputSystem.is_button_down(trigger_key):
                     
                    g_current_tick = self.get_tick_count()
                    if not _target.is_valid() and not get_best_target(view_angle, self):
                        continue
                    aim_at_closetarget(magnetic_smooth, view_angle, get_target_angle(self, _target, 8))
                #else:
                    #target_set(Player(0))
                    #
                    cross_id = self.get_cross_index()
                    if cross_id == 0:
                        continue
                    cross_target = Entity.get_client_entity(cross_id - 1)
                    if self.get_team_num() != cross_target.get_team_num() and cross_target.get_health() > 0:
                        
                        u32.mouse_event(0x0002, 50, 50, 50, 50)
                        
                        k32.Sleep(50)
                        
                      
                        u32.mouse_event(0x0004, 500, 500, 500, 500)
                     
                    
                if aim and InputSystem.is_button_down(aim_key):
                    
                    g_current_tick = self.get_tick_count()
                    
                    if not _target.is_valid() and not get_best_target(view_angle, self):
                        continue
                    aim_at_target(fl_sensitivity, view_angle, get_target_angle(self, _target, _target_bone))
                else:
                    
                    target_set(Player(0))
                if stdalone_rcs:
                    current_punch = self.get_vec_punch()
                    if self.get_shots_fired() > 1:
                        new_punch = Vector3(current_punch.x - g_old_punch.x,
                                            current_punch.y - g_old_punch.y, 0)
                        new_angle = Vector3(view_angle.x - new_punch.x * 1.9, view_angle.y - new_punch.y * 1.8, 0)
                        u32.mouse_event(0x0001,
                                        int(((new_angle.y - view_angle.y) / fl_sensitivity) / -0.022),
                                        int(((new_angle.x - view_angle.x) / fl_sensitivity) / 0.022),
                                        0, 0)
                    g_old_punch = current_punch
            except ValueError:
                continue
        else:
            g_previous_tick = 0
            target_set(Player(0))
            
     

