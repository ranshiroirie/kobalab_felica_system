# -*- coding: utf-8 -*-
import nfc
import binascii
import time
import sys

def on_connect(tag):
    #FelicaのID,PMM,SYSを読み取る
    ID = binascii.hexlify(tag.identifier).upper().decode("utf-8")
    PMM = binascii.hexlify(tag.pmm).upper().decode("utf-8")
    SYS = hex(tag.sys)[2:].upper()
    print("ID: %s"  % ID)
    print("PMM: %s"  % PMM)
    print("SYS: %s"  % SYS)

    #もし学生証なら
    if SYS == "809E":
        #学生証番号の取得
        sc = nfc.tag.tt3.ServiceCode(4, 0x010b)
        bc = nfc.tag.tt3.BlockCode(0, service=0)
        student_id = tag.read_without_encryption([sc], [bc])[:7].decode("utf-8")
        print("StudentID: %s" % student_id)
        #カード情報の照合

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
        'targets': ['212F', '424F'],
        'on-connect': on_connect
    }

    #読み取りの試行
    try:
        print("読み取り開始")
        clf.connect(rdwr=rdwr_options)
    #キーボード入力で終了
    except KeyboardInterrupt:
        go_to_exit()

if __name__ == '__main__':
    main()