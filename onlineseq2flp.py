# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: MIT

import blackboxprotobuf
import argparse
import json
import varint
import struct
from io import BytesIO

ols_insts = {}
ols_insts[43] = ["Electric Piano", 16033794]
ols_insts[41] = ["Grand Piano", 12543508]
ols_insts[17] = ["Harpsichord", 2184959]
ols_insts[25] = ["Ragtime Piano", 10503948]
ols_insts[26] = ["Music Box", 10395164]
ols_insts[0] = ["Elec. Piano (Classic)", 16033794]
ols_insts[8] = ["Grand Piano (Classic)", 12543508]
ols_insts[2] = ["Drum Kit", 1842359]
ols_insts[31] = ["Electric Drum Kit", 7368959]
ols_insts[19] = ["Xylophone", 3490548]
ols_insts[34] = ["Vibraphone", 13224276]
ols_insts[21] = ["Steel Drums", 7697781]
ols_insts[39] = ["8-Bit Drum Kit", 2166686]
ols_insts[40] = ["2013 Drum Kit", 1312130]
ols_insts[36] = ["808 Drum Kit", 4657023]
ols_insts[42] = ["909 Drum Kit", 16711833]
ols_insts[1] = ["Acoustic Guitar", 39423]
ols_insts[4] = ["Electric Guitar", 5222220]
ols_insts[48] = ["Bass", 2171169]
ols_insts[5] = ["Bass (Classic)", 2171169]
ols_insts[29] = ["Slap Bass", 2952965]
ols_insts[32] = ["Jazz Guitar", 3515808]
ols_insts[35] = ["Muted E-Guitar", 4161280]
ols_insts[38] = ["Distortion Guitar", 1983488]
ols_insts[49] = ["Clean Guitar", 1496032]
ols_insts[22] = ["Sitar", 44512]
ols_insts[33] = ["Koto", 30698]
ols_insts[3] = ["Smooth Synth", 6495976]
ols_insts[6] = ["Synth Pluck", 11882815]
ols_insts[7] = ["Scifi", 3726284]
ols_insts[13] = ["8-Bit Sine", 6513663]
ols_insts[14] = ["8-Bit Square", 6553461]
ols_insts[15] = ["8-Bit Sawtooth", 16769123]
ols_insts[16] = ["8-Bit Triangle", 16737276]
ols_insts[9] = ["French Horn", 1472386]
ols_insts[10] = ["Trombone", 60159]
ols_insts[11] = ["Violin", 6516108]
ols_insts[46] = ["Violin (Sustain)", 6516108]
ols_insts[12] = ["Cello", 2962255]
ols_insts[45] = ["Cello (Sustain)", 2962255]
ols_insts[18] = ["Concert Harp", 2186780]
ols_insts[20] = ["Pizzicato", 11723007]
ols_insts[23] = ["Flute", 12384744]
ols_insts[47] = ["Strings (Sustain)", 16741774]
ols_insts[24] = ["Saxophone", 5555880]
ols_insts[27] = ["Synth Bass", 8045598]
ols_insts[28] = ["Church Organ", 5185812]
ols_insts[30] = ["Pop Synth", 12055147]
ols_insts[37] = ["808 Bass", 0]

def int2float(value):
    return struct.unpack("<f", struct.pack("<i", value))[0]

def make_fl_event(flpbytes, value, data):
    if value <= 63 and value >= 0: # int8
        flpbytes.write(value.to_bytes(1, "little"))
        flpbytes.write(data.to_bytes(1, "little"))
    if value <= 127 and value >= 64 : # int16
        flpbytes.write(value.to_bytes(1, "little"))
        flpbytes.write(data.to_bytes(2, "little"))
    if value <= 191 and value >= 128 : # int32
        flpbytes.write(value.to_bytes(1, "little"))
        flpbytes.write(data.to_bytes(4, "little"))
    if value <= 224 and value >= 192 : # text
        flpbytes.write(value.to_bytes(1, "little"))
        flpbytes.write(varint.encode(len(data)))
        flpbytes.write(data)
    if value <= 255 and value >= 225 : # data
        flpbytes.write(value.to_bytes(1, "little"))
        flpbytes.write(varint.encode(len(data)))
        flpbytes.write(data)

def sortnotes(notelist):
    t_notelist_bsort = {}
    t_notelist_sorted = {}
    new_notelist = []
    for note in notelist:
        if note['p'] not in t_notelist_bsort: t_notelist_bsort[note['p']] = []
        t_notelist_bsort[note['p']].append(note)
    t_notelist_sorted = dict(sorted(t_notelist_bsort.items(), key=lambda item: item[0]))
    for t_notepos in t_notelist_sorted:
        for note in t_notelist_sorted[t_notepos]:
            new_notelist.append(note)
    return new_notelist

global t_notelist
t_notelist = {}

def parse_note(notedata):
    global t_notelist
    ols_pos = 0
    ols_inst = 0
    ols_vol = 1
    ols_note = int(notedata['1'])
    if '2' in notedata: ols_pos = int2float(int(notedata['2']))
    if '3' in notedata: ols_dur = int2float(int(notedata['3']))
    if '4' in notedata: ols_inst = int(notedata['4'])
    if '5' in notedata: ols_vol = int2float(int(notedata['5']))
    note = {}
    note['p'] = ols_pos
    note['k'] = ols_note
    note['d'] = ols_dur
    note['v'] = ols_vol
    if ols_inst not in t_notelist: t_notelist[ols_inst] = []
    t_notelist[ols_inst].append(note)

parser = argparse.ArgumentParser()
parser.add_argument("-i", default=None)
parser.add_argument("-o", default=None)
args = parser.parse_args()
in_file = args.i
out_file = args.o
if in_file == None: print('[error] An input file must be specified'); exit()
if out_file == None: print('[error] An output name must be specified'); exit()

flpout = open(out_file+'.flp', 'wb')

os_data_song_stream = open(in_file, 'rb')
os_data_song_data = os_data_song_stream.read()
message, typedef = blackboxprotobuf.protobuf_to_json(os_data_song_data)

os_data = json.loads(message)

os_notes = os_data["2"]
os_main = os_data["1"]

for os_note in os_notes:
    parse_note(os_note)

ppq = 96

ppqstep = ppq/4

numofchannels = len(t_notelist)
#FLhd
data_FLhd = BytesIO()
data_FLhd.write(numofchannels.to_bytes(3, 'big'))
data_FLhd.write(b'\x00')
data_FLhd.write(ppq.to_bytes(2, 'little'))

#FLdt
data_FLdt = BytesIO()
make_fl_event(data_FLdt, 199, '20.7.2.1852'.encode('utf8') + b'\x00')
make_fl_event(data_FLdt, 159, 1852)
make_fl_event(data_FLdt, 28, 1) #Registered
make_fl_event(data_FLdt, 37, 1)
make_fl_event(data_FLdt, 200, b'\x00\x00')
make_fl_event(data_FLdt, 156, int(float(int(os_main['1'])*1000)))
make_fl_event(data_FLdt, 67, 1) #CurrentPatNum
make_fl_event(data_FLdt, 9, 1) #LoopActive
make_fl_event(data_FLdt, 11, 0) #Shuffle 
make_fl_event(data_FLdt, 80, 0) #MainPitch
make_fl_event(data_FLdt, 17, 4) #Numerator
make_fl_event(data_FLdt, 18, 4) #Denominator
make_fl_event(data_FLdt, 35, 1)
make_fl_event(data_FLdt, 23, 1) #PanVolumeTab
make_fl_event(data_FLdt, 30, 1) #TruncateClipNotes
make_fl_event(data_FLdt, 10, 0) #ShowInfo
make_fl_event(data_FLdt, 197, "onlinesequencer.net".encode('utf-16le') + b'\x00\x00')
make_fl_event(data_FLdt, 194, "".encode('utf-16le') + b'\x00\x00') #Title
make_fl_event(data_FLdt, 206, "".encode('utf-16le') + b'\x00\x00') #Genre
make_fl_event(data_FLdt, 207, "".encode('utf-16le') + b'\x00\x00') #Author
make_fl_event(data_FLdt, 202, "".encode('utf-16le') + b'\x00\x00') #ProjectDataPath
make_fl_event(data_FLdt, 195, "".encode('utf-16le') + b'\x00\x00') #Comment
make_fl_event(data_FLdt, 231, "Unsorted".encode('utf-16le') + b'\x00\x00') #ChanGroupName

fl_arrangement = BytesIO()

flarr_patternbase = 20480
flarr_unknown1 = 120
flarr_unknown2 = 25664
flarr_unknown3 = 32896
flarr_flags = 4

flnote_flags = 16384
flnote_finep = 120
flnote_group = 0
flnote_u1 = 0
flnote_rel = 64
flnote_midich = 0
flnote_pan = 64
flnote_mod_x = 128
flnote_mod_y = 128

fltrki_color = 5656904
fltrki_icon = 0
fltrki_enabled = 1
fltrki_height = 1.0
fltrki_lockedtocontent = 255
fltrki_motion = 16777215
fltrki_press = 0
fltrki_triggersync = 0
fltrki_queued = 5
fltrki_tolerant = 0
fltrki_positionSync = 1
fltrki_grouped = 0
fltrki_locked = 0

channum = 0
for os_instnote in t_notelist:
    instid = os_instnote
    instnotes = sortnotes(t_notelist[os_instnote])
    make_fl_event(data_FLdt, 64, channum) #NewChan
    make_fl_event(data_FLdt, 21, 0) #ChanType
    make_fl_event(data_FLdt, 203, ols_insts[instid][0].encode('utf-16le') + b'\x00\x00') #PluginName
    make_fl_event(data_FLdt, 128, ols_insts[instid][1]) #Color

    make_fl_event(data_FLdt, 65, int(channum+1)) 
    make_fl_event(data_FLdt, 150, ols_insts[instid][1]) #PatColor
    make_fl_event(data_FLdt, 193, ols_insts[instid][0].encode('utf-16le') + b'\x00\x00') #PatName

    flarr_itemindex = int(channum+1 + flarr_patternbase)
    flarr_trackindex = (-500 + int(channum+1))*-1

    fl_arrangement.write(b'\x00\x00\x00\x00')
    fl_arrangement.write(flarr_patternbase.to_bytes(2, 'little'))
    fl_arrangement.write(flarr_itemindex.to_bytes(2, 'little'))
    fl_arrangement.write(b'\xff\xff\xff\xff')
    fl_arrangement.write(flarr_trackindex.to_bytes(4, 'little'))
    fl_arrangement.write(flarr_unknown1.to_bytes(2, 'little'))
    fl_arrangement.write(flarr_flags.to_bytes(2, 'little'))
    fl_arrangement.write(flarr_unknown2.to_bytes(2, 'little'))
    fl_arrangement.write(flarr_unknown3.to_bytes(2, 'little'))
    fl_arrangement.write(b'\xff\xff\xff\xff')
    fl_arrangement.write(b'\xff\xff\xff\xff')

    fl_patternnotes = BytesIO()
    for instnote in instnotes:
        flnote_pos = int(instnote['p']*ppqstep)
        flnote_rack = channum
        flnote_dur = int(instnote['d']*ppqstep)
        flnote_key = int(instnote['k'])
        flnote_velocity = max(0, min(128, int(instnote['v']*100)))

        fl_patternnotes.write(flnote_pos.to_bytes(4, 'little'))
        fl_patternnotes.write(flnote_flags.to_bytes(2, 'little'))
        fl_patternnotes.write(flnote_rack.to_bytes(2, 'little'))
        fl_patternnotes.write(flnote_dur.to_bytes(4, 'little'))
        fl_patternnotes.write(flnote_key.to_bytes(2, 'little'))
        fl_patternnotes.write(flnote_group.to_bytes(2, 'little'))
        fl_patternnotes.write(flnote_finep.to_bytes(1, 'little'))
        fl_patternnotes.write(flnote_u1.to_bytes(1, 'little'))
        fl_patternnotes.write(flnote_rel.to_bytes(1, 'little'))
        fl_patternnotes.write(flnote_midich.to_bytes(1, 'little'))
        fl_patternnotes.write(flnote_pan.to_bytes(1, 'little'))
        fl_patternnotes.write(flnote_velocity.to_bytes(1, 'little'))
        fl_patternnotes.write(flnote_mod_x.to_bytes(1, 'little'))
        fl_patternnotes.write(flnote_mod_y.to_bytes(1, 'little'))
    fl_patternnotes.seek(0)
    make_fl_event(data_FLdt, 224, fl_patternnotes.read()) #PatternNotes
    channum += 1

fl_arrangement.seek(0)
make_fl_event(data_FLdt, 99, 0) #NewArrangement
make_fl_event(data_FLdt, 241, "Sequence".encode('utf-16le') + b'\x00\x00') #ArrangementName
make_fl_event(data_FLdt, 36, 0)
make_fl_event(data_FLdt, 233, fl_arrangement.read()) #PlayListItems

channum = 1
for os_instnote in t_notelist:
    instid = os_instnote
    fl_trackinfo = BytesIO()
    fl_trackinfo.write(channum.to_bytes(4, "little"))
    fl_trackinfo.write(ols_insts[instid][1].to_bytes(4, "little"))
    fl_trackinfo.write(fltrki_icon.to_bytes(4, "little"))
    fl_trackinfo.write(fltrki_enabled.to_bytes(1, "little"))
    fl_trackinfo.write(struct.pack('<f', fltrki_height))
    fl_trackinfo.write(fltrki_lockedtocontent.to_bytes(1, "little"))
    fl_trackinfo.write(fltrki_motion.to_bytes(4, "little"))
    fl_trackinfo.write(fltrki_press.to_bytes(4, "little"))
    fl_trackinfo.write(fltrki_triggersync.to_bytes(4, "little"))
    fl_trackinfo.write(fltrki_queued.to_bytes(4, "little"))
    fl_trackinfo.write(fltrki_tolerant.to_bytes(4, "little"))
    fl_trackinfo.write(fltrki_positionSync.to_bytes(4, "little"))
    fl_trackinfo.write(fltrki_grouped.to_bytes(1, "little"))
    fl_trackinfo.write(fltrki_locked.to_bytes(1, "little"))
    fl_trackinfo.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\x01\x00\x00\x00\x00')
    fl_trackinfo.seek(0)
    make_fl_event(data_FLdt, 238, fl_trackinfo.read()) #TrackInfo
    make_fl_event(data_FLdt, 239, ols_insts[instid][0].encode('utf-16le') + b'\x00\x00') #TrackName
    channum += 1

data_FLhd.seek(0)
flpout.write(b'FLhd')
data_FLhd_out = data_FLhd.read()
flpout.write(len(data_FLhd_out).to_bytes(4, 'little'))
flpout.write(data_FLhd_out)

data_FLdt.seek(0)
flpout.write(b'FLdt')
data_FLdt_out = data_FLdt.read()
flpout.write(len(data_FLdt_out).to_bytes(4, 'little'))
flpout.write(data_FLdt_out)

