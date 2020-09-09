"""
This is application bootstrap file.
This file contain imports of all necessary libraries of python.
Also this bootstrap file cover all startup functionality of this application.
"""
# ========== Importing Necessary Libraries ==========
from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import random
import json
import winsound
# ===================================================

# ========== Reading Json Configuration File ==========
with open("project_config.json", "r") as config_file:
    params = json.load(config_file)["params"]
# =====================================================

# ========== Making the object of Flask Class ==========
app = Flask("Online Inventory Management And Forecasting System")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ======================================================

# ========== Setting A Secret Key For Application ==========
app.secret_key = str(params["application_secret_key"])  # str(random.randint(1, 99))
# ==========================================================

# ========== Making Object of SQLAlchemy Class And Connecting To Database ==========
if params["local_host"] == "true":
    app.config["SQLALCHEMY_DATABASE_URI"] = params["local_host_uri"]
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["prod_uri"]

# ===== Making db a object of SQLAlchemy Class =====
db = SQLAlchemy(app)
# ==================================================

# ==================== Settings For Mail ===================
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT="465",
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params["mail-username"],
    MAIL_PASSWORD=params["mail-password"]
)
# ==================== Setting For Mail ===================

# ===== Making mail a object of Mail Class =====
mail = Mail(app)
# ==============================================

# ===== Setting Configuration For Upload Folder =====
app.config["IMG_UPLOAD_FOLDER"] = params["image_upload_folder_url"]
# ===================================================================================


# ===== Function To Create Sound =====
def make_sound():
    winsound.MessageBeep(-1)
# ======================================
