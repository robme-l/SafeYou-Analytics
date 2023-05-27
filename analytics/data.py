# file for fetching data

from sqlalchemy import URL, create_engine
from sqlalchemy.sql import text
import pandas as pd


# ------- CREDENTIALS ------- #
DB_TYPE = 'mysql+mysqldb'
DB_HOST = 'safeyouanalytics.mysql.pythonanywhere-services.com'
DB_USER = 'safeyouanalytics'
DB_PASS = '$afeYou2'
DB_NAME = 'safeyouanalytics$default'
# ------ END CREDENTIALS ----- #

# -------- DB ACCESS --------- #
url_object = URL.create(
    DB_TYPE,username=DB_USER,password=DB_PASS,
    host=DB_HOST,database=DB_NAME
)
ENGINE = create_engine(url_object)
# ------- END DB ACCESS ------- #

def fetch_query(query,datetime_columns=[]):
    df = None
    with ENGINE.connect() as conn: # handles connection
        try:
            df = pd.DataFrame(conn.execute(text(query)).fetchall())
            for col in datetime_columns:
                df[col] = pd.to_datetime(df[col])
        except Exception as e:
            print(e)

    return df

def clean_data(df,cleanops=[],verbose=False):
    if not (df is None):
        for desc,op in cleanops.items():
            df = op(df)
            if verbose:
                print(desc)
    return df

def get_userpage_data():
    query = """
            SELECT * FROM users;
            """
    datetime_columns = ["birthday","created_at","updated_at","deleted_at"]
    cleanops = {"Remove test first_name accounts": lambda df: df[df["first_name"].str.lower() != "test"],
                "Remove test last_name accounts": lambda df: df[df["last_name"].str.lower() != "test"],
                "Remove test nickname accounts": lambda df: df[df["nickname"].str.lower() != "test"],
                }
    columns = ["id","role","is_verifying_otp","deleted_at",
               "first_name","last_name","nickname","updated_at","created_at",
               "device_type","language_id","birthday","marital_status"]

    df = clean_data(fetch_query(query,datetime_columns),cleanops)
    df = df[columns]
    df = preprocess_userpage(df)
    return df

def preprocess_userpage(df):
    # language encodings
    lang_enc = {1:"English",2:"Armenian",3:"Russian"}
    # marital status encodings
    marital_enc = {-1:"Not Selected",0:"Not Married",1:"Married"}
    # OS encoding
    os_enc = {1:"Android",None:"iOS"}
    # World Bank Age conversion
    def age_enc(x):
        if pd.isnull(x):
            return x
        elif x >= 65:
            return "65+"
        else:
            m = int((x // 5)*5)
            return f"{m}-{m+4}"
    
    # time filter
    time_filter = "created_at"

    # create age column
    y1,y2 = pd.Timestamp.today().year, df["birthday"].dt.year
    m1,m2 = pd.Timestamp.today().month, df["birthday"].dt.month
    d1,d2 = pd.Timestamp.today().day, df["birthday"].dt.day
    age = y1 - y2 - ((m1 < m2) | ((m1 == m2) & (d1 < d2))).astype(int)
    age.name = "age"
    df["age"] = df["age_bucket"] = age

    encodings = {
        ("language_id"):lang_enc,
        ("marital_status"):marital_enc,
        ("device_type"):os_enc,
        ("age_bucket"):age_enc,
    }
    for col,enc in encodings.items():
        df[col] = df[col].map(enc)

    return df
