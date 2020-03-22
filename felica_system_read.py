# -*- coding: utf-8 -*-
import nfc
import binascii
import time
import pymysql.cursors
import datetime
import sys
from DB_parameter.DB_parameter import *

Device = "test01"

#前回かざしたICの情報
BID = "0"
BPMM = "0"
BSYS = "0"

#データベースへ接続する関数
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
    global BID,BPMM,BSYS

    #データベースにログを送信するためのタイムスタンプの記録
    Timestamp = datetime.datetime.today()

    #FelicaのID,PMM,SYSを読み取る
    ID = binascii.hexlify(tag.identifier).upper().decode("utf-8")
    PMM = binascii.hexlify(tag.pmm).upper().decode("utf-8")
    SYS = hex(tag.sys)[2:].upper()

    #前回のFelicaと一緒ならパスする
    if ID == BID and PMM == BPMM and SYS == BSYS:
        print ("認証済み")
    else:
        #もし学生証なら
        if SYS == "809E":
            #学生証番号の取得
            sc = nfc.tag.tt3.ServiceCode(4, 0x010b)
            bc = nfc.tag.tt3.BlockCode(0, service=0)
            student_id = tag.read_without_encryption([sc], [bc])[:7].decode("utf-8")
            print("StudentID: %s" % student_id)
            #カード情報の照合
            try:
                cursor.execute("SELECT * from auth_id where ID='%s' and PMM='%s' and SYS='%s' and StudentID='%s'" % (ID,PMM,SYS,student_id))
                table = cursor.fetchall()
            #接続失敗なら照合結果を空で返す
            except pymysql.err.OperationalError:
                print("データーベース接続失敗")
                table = ()

            #照合結果なら空なら
            if table == ():
                #未登録として返す
                print("\n*** 未登録ID ***\n")
            #認証済みなら
            else:
                # cursor.execute("INSERT INTO stamp (Timestamp, Device, CardType, StudentID, ID, PMM, SYS) value (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")" % (Timestamp,Device,"StudentCard",student_id,ID,PMM,SYS))
                # conn.commit()
                #認証IDで返す
                print("\nOOO 認証ID => %s OOO\n" % student_id)

        #それ以外のICカードなら
        else:
            #カード情報の照合
            try:
                cursor.execute("SELECT StudentID from auth_id where ID='%s' and PMM='%s' and SYS='%s'" % (ID,PMM,SYS))
                table = cursor.fetchall()
            #接続失敗なら照合結果を空で返す
            except pymysql.err.OperationalError:
                print("データベース接続失敗")
                table = ()

            #照合結果なら空なら
            if table == ():
                #未登録として返す
                print("\n*** 未登録ID ***\n")
            #認証済みなら
            else:
                #交通系ICなら
                if SYS == "3":
                    felica_type = "Suica/PASMO"
                #おサイフケータイなら   
                elif SYS == "FE00":
                    felica_type = "Smartphone"
                #その他ICカードなら
                else:
                    felica_type = "Another IC card"
                #データベースで照合した学生証番号の取得
                rec_studentID = str(table)[3:-5]
                # cursor.execute("INSERT INTO stamp (Timestamp, Device, CardType, StudentID, ID, PMM, SYS) value (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")" % (str(Timestamp),Device,felica_type,rec_studentID,ID,PMM,SYS))
                # conn.commit()
                print("\nOOO 認証ID => %s (Type => %s) OOO\n" % (rec_studentID,felica_type))
    BID = ID
    BPMM = PMM
    BSYS = SYS

#プログラムの終了処理をする関数
def go_to_exit():
    print("終了処理中")
    #プログラムの終了
    sys.exit()

def main():
    print("メインプログラム稼働")
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
        'on-connect': on_connect
    }

    #読み取りの試行
    try:
        print("読み取り開始")
        while True:
            #タイムアウト処理の関数
            after1s = lambda : time.time() - startedtime > 0.1
            #経過時間の記録
            startedtime = time.time()
            #タイムアウトするまでリーダーの読み取り待機
            clf.connect(rdwr=rdwr_options, terminate=after1s)
            print("待機中")
            time.sleep(0.5)
    #キーボード入力で終了
    except KeyboardInterrupt:
        go_to_exit()

if __name__ == '__main__':
    db_connect()
    main()