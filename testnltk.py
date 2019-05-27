
import nltk
import pdfbox
import mysql.connector
import pandas as pd

from string import punctuation
from nltk.corpus import stopwords
from mysql.connector import errorcode





#######################################################################
############################   FUNÇÕES   #############################
#######################################################################

# Read PDF or String and return raw values
def _readRaw(path, tipo):
    if tipo == 'PDF':
        p = pdfbox.PDFBox()
        text = p.extract_text(path)
        return text
    elif tipo == "text":
        return path


# Tokenize text
def _tokenizer(text):
    tknzr = nltk.TweetTokenizer()
    textTknzr = tknzr.tokenize(text)
    return textTknzr

# Remove STOPWORD and Punctuation
def _clearText(text):
    stopwordsGeneric = set(list(punctuation) + stopwords.words('portuguese'))
    cleanText = [palavra for palavra in text if palavra not in stopwordsGeneric]
    return cleanText

# Stemmer text
def _stemmerText(text):
    stemmerText = []
    stemmer = nltk.RSLPStemmer()
    for w in text:
        stemmerText.append(stemmer.stem(w))
    return stemmerText

# return List with Frequency distribuition of words and set text title to list
def _freqDist(text, textTitle):
    freqDistList = []
    freqDist = nltk.FreqDist(text)
    listKeys = list(freqDist.keys())
    listValues  = list(freqDist.values())

    for i in range(len(freqDist.items())):
        freqDistList.append((listKeys[i], str(listValues[i]),textTitle))

    return list(freqDistList)


def connectDB(userDB, db):
    try:
        cnx = mysql.connector.connect(user=userDB, database=db)
        return cnx

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cnx.close()

def persistData(cursor, cnx,freqDistList):
    table = "dados"
    sql = "INSERT INTO " + table + " (keyWord, quant, nome) VALUES (%s, %s, %s)"
    cursor.executemany(sql, freqDistList)
    cnx.commit()
    print(cursor.rowcount, "Values added")


#      (1)Parameter: "PDF"/"text";
#      (2)Parameter: If "PDF": pass file path as parameter, if "text": pass String direct as parameter;
#      (3)Parameter: title of text or PDF file
def _prepareText(tipo, path, textTitle):
    text = _readRaw(path,tipo)
    textTknzr = _tokenizer(text)
    clearText = _clearText(textTknzr)
    stemmerText = _stemmerText(clearText)
    freqDistList = _freqDist(stemmerText, textTitle)

    return freqDistList

def getDataFromDB():
    cursor.execute("SELECT * FROM dados")
    result = cursor.fetchall()
    keys = []
    quant = []
    nome = []
    for i in result:
        keys.append(i[0])
        quant.append(i[1])
        nome.append(i[2])
        print(i)
    return keys, quant, nome




def exportToXlsx(output, keys, quant, nome):
    # Create a Pandas dataframe from some data.
    df = pd.DataFrame({'KeysWord': keys,
                       'Quant': quant,
                       'Nome': nome,
                       })

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(output+".xlsx", engine='xlsxwriter')

    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name='Sheet1')

    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    writer.save()





dirPDF = 'C:/Users/Lucas/Desktop/PNL/PDF/livro_2.pdf'

textToPersist = _prepareText('PDF', dirPDF, "texto03")

# Connect DATABASE
cnx = connectDB('root', 'npl')
if (cnx):
    print("Processing...")
    cursor = cnx.cursor(prepared=True)
    persistData(cursor, cnx, textToPersist)


    # Returns of getDataFromDB()
    # keyWords, quant, nome = getDataFromDB()
    #
    # pathExcel = "C:/Users/Lucas/Desktop/PNL/FileExcelNew"
    # exportToXlsx(pathExcel, keyWords, quant, nome)
else:
    print("Error")
