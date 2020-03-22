# -*- coding: utf-8 -*-
import nfc
import binascii
import time
import pymysql.cursors
import sys
from DB_parameter import *

def db_connect():
    #他の関数でも使用できるようにする
    global conn, cursor

    print("データベースへ接続中...")
    #接続の試行
    try:
        #データベースへの接続
        conn = pymysql.connect(host=HOST_IP_ADDRESS, user=DB_USER, password=DB_PASSWORD, db=DATABSE, charset="utf8")
        cursor = conn.cursor()
    #接続エラー
    except pymysql.err.OperationalError:
        print("ネットワーク接続失敗！接続状況と設定情報を確認して下さい")
        #終了処理
        go_to_exit()

#Felicaを読み取った時に処理をする関数
def on_connect(tag):
    global student_id
    #FelicaのID,PMM,SYSを読み取る
    ID = binascii.hexlify(tag.identifier).upper().decode("utf-8")
    PMM = binascii.hexlify(tag.pmm).upper().decode("utf-8")
    SYS = hex(tag.sys)[2:].upper()
    print("ID: %s" % ID)
    print("PMM: %s" % PMM)
    print("SYS: %s" % SYS)
    #もし学生証でなければ
    if SYS != "809E":
        print("学生証をタッチしてください")
        while SYS != "809E":
            #学生証が読み取れるまで繰り返す
            rdwr_options = {
                'targets': ['212F' , '424F'],
                'on-connect': re_connect,
            }
            clf.connect(rdwr=rdwr_options)
            if RESYS == "809E":
                break
    else:
        #学生証番号の取得
        sc = nfc.tag.tt3.ServiceCode(4, 0x010b)
        bc = nfc.tag.tt3.BlockCode(0, service=0)
        student_id = tag.read_without_encryption([sc], [bc])[:7].decode("utf-8")
        print("StudentID: %s" % student_id)
    #データベースへの登録
    sql = ("INSERT INTO auth_id(ID, PMM, SYS, StudentID) values ('%s','%s','%s','%s') ON DUPLICATE KEY UPDATE ID = VALUES(ID)" % (ID,PMM,SYS,student_id))
    cursor.execute(sql)
    print(sql)
    conn.commit()

#2回目以降の読み取り関数
def re_connect(tag):
    global student_id, RESYS
    #FelicaのID,PMM,SYSを読み取る
    ID = binascii.hexlify(tag.identifier).upper().decode("utf-8")
    PMM = binascii.hexlify(tag.pmm).upper().decode("utf-8")
    RESYS = hex(tag.sys)[2:].upper()
    if RESYS == "809E":
        #学生証番号の取得
        sc = nfc.tag.tt3.ServiceCode(4, 0x010b)
        bc = nfc.tag.tt3.BlockCode(0, service=0)
        student_id = tag.read_without_encryption([sc], [bc])[:7].decode("utf-8")
        print("StudentID: %s" % student_id)

#プログラムの終了処理をする関数
def go_to_exit():
    print("終了処理中")
    #プログラムの終了
    sys.exit()

def main():
    global clf
    print("登録プログラム稼働")
     #リーダーへの接続を試行
    try:
        #リーダーへの接続
        clf = nfc.ContactlessFrontend("usb")
    #接続エラー
    except IOError:
        print("リーダーが接続されていません")
        #終了処理
        go_to_exit()
    print("リーダーの接続完了")

    #リーダーでFelicaを読み取る設定
    rdwr_options = {
        'targets': ['212F' , '424F'],
        'on-connect': on_connect,
    }

    #読み取り開始
    print("読み取り開始")
    clf.connect(rdwr=rdwr_options)

if __name__ == '__main__':
    db_connect()
    main()
