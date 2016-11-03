import re                   #정규 표현식(Regular Expression)
import psycopg2             #python - postgre sql 연결 모듈
from glob import glob       #파일 검색 simmilar ls
import os.path              #파일명 추출

#DB연결
conn=psycopg2.connect(database='jmdic', user='postgres', password='tpdltja1!', host='jycom.asuscomm.com', port='3432', sslmode='require')

#커서 생성
cur = conn.cursor()

# cur.execute("select * from sublist; ")
# print(cur.fetchone())
#
# cur.close()
# conn.close()


#영상 리스트 생성
def getMno(subName):

    #영상 이름 추출
    movieName = re.findall('(.*?EP\d+).',subName, re.IGNORECASE)[0]
    #DB에서 중복 여부 확인
    cur.execute("select 1 from movielist where mtitle = %s limit 1;", (movieName,))

    #중복이 아닐 시 DB에 삽입
    if(not cur.fetchall()):
        cur.execute("INSERT INTO movielist (mtitle) VALUES (%s);", (movieName,))
        cur.execute("SELECT LASTVAL()")
        mno = cur.fetchone()[0]
        #print("a"+str(mno))
        return mno
    #중복일 시 인덱스 번호 검색
    else:
        cur.execute("select mno from movielist where mtitle = (%s);", (movieName,))
        mno = cur.fetchone()[0]
        #print("b"+str(mno))
        return mno

def makeKdic():
    f = glob('./'+title+'/*.kor.smi')
    for i in range (len(f)):
        with open (f[i], 'rb') as r:
            try:
                subtitle = r.read().decode('utf-8')

            except UnicodeDecodeError:
                with open (f[i], 'r', encoding="utf-16") as r:
                    subtitle = r.read()
            subtitle = re.sub('<sync start=(\d+?)><P Class=.+>&nbsp;', '', subtitle, count=0, flags=re.I)
            subtitle = re.sub('<P Class=.+?>', '<P Class=KRCC>', subtitle, count=0, flags=re.I)
            subtitle = re.sub('<br>', '', subtitle, count=0, flags=re.I)
            subtitle = re.sub('<font.+>', '', subtitle, count=0, flags=re.I)
            subtitle = re.sub('<b>', '', subtitle, count=0, flags=re.I)
            subtitle = re.sub('<i>', '', subtitle, count=0, flags=re.I)
            subName = os.path.basename(r.name)
            print(subName + "登録完了")
            mno = getMno(subName)
            krcc = re.findall(r'start=(\d+?)><P Class=KRCC>(.*?)<SYNC', subtitle, re.MULTILINE|re.DOTALL|re.IGNORECASE)
            #print(krcc)
            cur.execute("INSERT INTO sublist (mno, lan, subtitle) VALUES (%s, %s, %s)", (mno, "k", subName,))
            cur.execute("SELECT LASTVAL()")
            subno = cur.fetchone()[0]
            for i in range(len(krcc)):
                sync = int(int(krcc[i][0])/1000)
                subKorText = krcc[i][1]
                #print(subKorText)
                cur.execute("INSERT INTO subcontent (subno, sync, subcontent) VALUES (%s, %s, %s)", (subno, sync, subKorText))
        conn.commit()



def makeJdic():
    f = glob('./'+title+'/*.jpn.srt')
    for i in range (len(f)):
        with open (f[i], 'rb') as r:
            subtitle = r.read().decode('utf-8')
            #remove multi line
            #subtitle = re.sub('\r', '\n', subtitle, count=0, flags=re.I)
            subName = os.path.basename(r.name)
            print(subName + "登録完了")
            mno = getMno(subName)
            #lf
            jpcc = re.findall(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3}\n+)(.*?)\n+', subtitle, re.MULTILINE|re.DOTALL|re.IGNORECASE)
            if(len(jpcc) < 10):
                #crlf
                jpcc = re.findall(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3}\r\n)(.*?)\r\n\r\n', subtitle, re.MULTILINE|re.DOTALL|re.IGNORECASE)

            #print(jpcc)
            cur.execute("INSERT INTO sublist (mno, lan, subtitle) VALUES (%s, %s, %s)", (mno, "j", subName,))
            cur.execute("SELECT LASTVAL()")
            subno = cur.fetchone()[0]
            for i in range(len(jpcc)):
                sync = re.findall('(\d{2}):(\d{2}):(\d{2}),(\d{3})', jpcc[i][0])
                sync = int(sync[0][0])*3600 + int(sync[0][1]) * 60 + int(sync[0][2])
                subJpnText = jpcc[i][2]
                #print(subJpnText)
                cur.execute("INSERT INTO subcontent (subno, sync, subcontent) VALUES (%s, %s, %s)", (subno, sync, subJpnText))
        conn.commit()

def search():
    print("キーワードを入力してください")
    searchTxt = input()
    #if len(searchTxt) <= 2:
   #    print("단어를 입력해 주세요")
   #    exit()

    #else:
    print("キーワード : " + searchTxt)
    searchTxt = '%' + searchTxt + '%'
    curSearch  = conn.cursor()
    curSearch.execute("SELECT subno, sync, subcontent from subcontent WHERE subcontent LIKE (%s)", (searchTxt,))
    search_result = curSearch.fetchall()
    for i in range (len(search_result)):
        print(str(i) + " : " + str(search_result[i]))

    print("字幕選択")
    subindex = int(input())
    subNumbF = int(search_result[subindex][0])
    #print("첫번쨰 자막 번호 : " + str(subNumbF))

    subSync = search_result[subindex][1]
    #print("Sync" + str(subSync))

    curSearch.execute("select subno from sublist where mno = (select mno from sublist where subno = (%s)) AND subno != (%s)", (subNumbF, subNumbF,))
    subNumbS = curSearch.fetchone()
    curSearch.execute("SELECT subno, sync, subcontent from subcontent WHERE subno IN ((%s),(%s)) AND subcontent.sync BETWEEN (%s) and (%s)",(subNumbF, subNumbS, int(subSync)-3, int(subSync)+3,))
    search_result = curSearch.fetchall()

    print("検索結果")
    for i in range(len(search_result)):
        print(search_result[i])


print("0 = 字幕登録, 1 = 検索")
sw = input()

if(sw == "0"):

    print("タイトルを入力してください")
    title = input()
    #print(cur.fetchall())
    makeKdic()
    makeJdic()


elif(sw == "1"):
    search()
