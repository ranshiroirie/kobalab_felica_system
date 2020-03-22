# 学生証対応Felicaデータベースシステム


＜必要なもの・要件＞

・ソニー SONY 非接触ICカードリーダー/ライター PaSoRi RC-S380

・MacもしくはPC

・Python3が導入されている


＜初期設定＞

・pip3 install pymysql nfcpy を実行して必要なモジュールをインストールする

・libusbをインストールする
（MacでHomebrewを導入している人はbrew install libusbを実行、ubuntuを使用している人はsudo apt-get install libusbを実行、それ以外については方法を調べること）


＜データベース接続用の設定ファイルについて＞

MySQLなどのデータベースを使用する場合、DB_parameter.pyの各項目の情報が正しく入力されていること。
