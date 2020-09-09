"""
This file provide data layer between application and mysql database
This file contain models of Tables and manage data using orm methods
This file contain several function that get data in different manner and format as required
"""
# ========== Try Block To Import Files ==========
# This try block will check for all files that are being importing.
# If any of file is missing it terminates the app
try:
    from bootstrap import db, app, session, random
    from sqlalchemy import desc, func, asc
    from os import remove  # for previous files deleting
    from datetime import datetime, date, timedelta
except FileExistsError or FileNotFoundError or ImportError:
    print("Please Check For Other Files Or DB Object In Bootstrap File Code")
    exit()
# ===============================================
# Note :  All of these classes represent database tables
# ========== Database Model Classes ==========


# ==================== Logs Class ====================
class Logs(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    action = db.Column("action", db.String(250), nullable=False)
    performed_by = db.Column("performed_by", db.String(250), nullable=False)
    user_type = db.Column("user_type", db.String(10), nullable=False)
    date = db.Column("date", db.String(30), nullable=False)
    only_date = db.Column("only_date", db.String(15), nullable=False)

    @staticmethod
    def get_logs():
        all_logs = Logs.query.order_by(desc(Logs.sno)).all()
        return all_logs

    @staticmethod
    def save_log(action, user_type, by):
        simple_date = datetime.today().strftime('%d/%m/%Y')
        date_now = datetime.now()
        date_now = date_now.strftime("%d/%m/%Y %H:%M:%S")
        log = Logs(action=action, performed_by=by, user_type=user_type, date=date_now, only_date=simple_date)
        db.session.add(log)
        db.session.commit()

    @staticmethod
    def get_this_user_logs(performed_by):
        user_logs = Logs.query.filter_by(performed_by=performed_by).filter_by(user_type="user").all()
        return user_logs

    @staticmethod
    def get_this_date_logs(of_date):
        logs = Logs.query.filter_by(only_date=of_date).all()
        return logs

    @staticmethod
    def clear_one_date_logs(of_date):
        print(of_date)
        format_date = str(of_date)
        of_date = format_date[8:] + "/" + format_date[5:7] + "/" + format_date[:4]
        print(of_date)
        all_logs_to_delete = Logs.get_this_date_logs(of_date)
        if all_logs_to_delete:
            for logs in all_logs_to_delete:
                db.session.delete(logs)
            db.session.commit()
            return True
        else:
            return False

    @staticmethod
    def clear_range_date_logs(from_date, to_date):
        # please do not try to understand, this code is just to check that 'from' date is not greater then 'to'E date
        from_date = str(from_date)[8:] + "/" + str(from_date)[5:7] + "/" + str(from_date[:4])
        to_date = str(to_date)[8:] + "/" + str(to_date)[5:7] + "/" + str(to_date[:4])
        if int(from_date[:2]) > int(to_date[:2]):
            if int(from_date[3:5]) > int(to_date[3:5]):
                if int(from_date[6:]) > int(to_date[6:]):
                    return False
        elif int(from_date[3:5]) > int(to_date[3:5]):
            if int(from_date[6:]) > int(to_date[6:]):
                return False
        elif int(from_date[6:]) > int(to_date[6:]):
            return False
        else:
            logs_to_delete = Logs.query.filter(Logs.only_date >= from_date).filter(Logs.only_date <= to_date).all()
            if logs_to_delete:
                for log in logs_to_delete:
                    db.session.delete(log)
                db.session.commit()
                return True
            else:
                return False
# ==================== Logs Class Ends Here ====================


# ==================== Users Class ====================
class Users(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    user_name = db.Column("user_name", db.String(50), nullable=False)
    user_gender = db.Column("user_gender", db.String(8), nullable=False)
    user_id = db.Column("user_id", db.String(20), nullable=False)
    user_password = db.Column("user_password", db.String(20), nullable=False)
    user_status = db.Column("user_status", db.String(15), nullable=False)
    working_store_id = db.Column("working_store_id", db.String(5), nullable=False)
    user_phno = db.Column("user_phno", db.String(12), nullable=False)
    user_hiredate = db.Column("user_hiredate", db.Date, nullable=False)
    user_email = db.Column("user_email", db.String(50), nullable=True)
    user_address = db.Column("user_address", db.String(120), nullable=True)

    @staticmethod
    def validate_user(entered_username, entered_password):  # return true if user exist in database
        user = Users.query.filter_by(user_id=entered_username).first()
        if user:
            if user.user_password == entered_password:
                if user.user_status == "Active":
                    if user.working_store_id != "":
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False

    @staticmethod
    def get_user_data(user_id):
        user_data = Users.query.filter_by(user_id=user_id).first()
        return user_data

    @staticmethod
    def get_all_user_data():
        users_data = Users.query.all()
        return users_data

    @staticmethod
    def count_users(store_id):  # count users of specific store
        no_of_users = Users.query.filter_by(working_store_id=store_id).all()
        return len(no_of_users)

    @staticmethod
    def save_new_user(user_id, password, name, phno, hiredate, gender, status, store_id, email, address):
        if Users.get_user_data(user_id):
            return False
        save_query = Users(user_name=name, user_gender=gender, user_id=user_id, user_password=password,
                           user_status=status, working_store_id=store_id, user_phno=phno, user_hiredate=hiredate,
                           user_email=email, user_address=address)

        db.session.add(save_query)
        db.session.commit()
        return True

    @staticmethod
    def update_user(old_id, new_id, password, name, phno, hiredate, gender, status, store_id, email, address):
        user_data = Users.get_user_data(old_id)
        if old_id != new_id:
            if Users.get_user_data(new_id):
                return False
        user_data.user_id = new_id
        user_data.user_password = password
        user_data.user_name = name
        user_data.user_phno = phno
        user_data.user_hiredate = hiredate
        user_data.user_gender = gender
        user_data.user_status = status
        user_data.working_store_id = store_id
        user_data.user_email = email
        user_data.user_address = address
        db.session.commit()
        # Now update selling details
        user_invoices = Invoices.get_this_user_invoices(old_id)
        for user_invoice in user_invoices:
            user_invoice.prod_sold_by = new_id
        db.session.commit()
        # ==========================
        # Updating Users Logs
        user_logs = Logs.get_this_user_logs(old_id)
        for log in user_logs:
            log.performed_by = new_id
        db.session.commit()
        # ==================
        # Updating User Messages
        user_messages = Messages.get_messages_for(old_id)
        for message in user_messages:
            message.message_to = new_id
        db.session.commit()
        user_send_messages = Messages.get_send_messages(old_id)
        for message in user_send_messages:
            message.message_from = new_id
        db.session.commit()
        # ======================
        # Updating User Reports
        user_reports = ReportsDraft.get_reports_by(old_id)
        for report in user_reports:
            report.gen_by = new_id
        db.session.commit()
        # =====================
        return True

    @staticmethod
    def delete_this_user(user_id):
        user_to_delete = Users.get_user_data(user_id)
        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()
            return True
        else:
            return False

    @staticmethod
    def generate_user_dashboard_data():
        total_brands = Brands.query.count()
        active_brands = Brands.query.filter_by(brand_status="Active").count()
        unactive_brands = Brands.query.filter_by(brand_status="UnActive").count()
        total_messages = Messages.query.filter_by(message_to=session["user"]).count()
        unread_messages = Messages.query.filter_by(message_to=session["user"]).filter_by(status="UnRead").count()
        readed_messages = Messages.query.filter_by(message_to=session["user"]).filter_by(status="Readed").count()
        total_products = Products.query.count()
        out_of_order_prod = Products.query.filter(Products.qty_remain <= 0).count()
        near_to_out_of_order_prod = Products.query.filter(Products.qty_remain >= 1).filter(Products.qty_remain <= 20) \
            .count()
        recent_activities = Logs.get_this_user_logs(session["user"])
        dashboard_data = {
            "total_brands": total_brands,
            "active_brands": active_brands,
            "unactive_brands": unactive_brands,
            "total_messages": total_messages,
            "unread_messages": unread_messages,
            "readed_messages": readed_messages,
            "total_prod": total_products,
            "out_of_order_prod": out_of_order_prod,
            "near_to_out_of_order_prod": near_to_out_of_order_prod,
            "recent_activities": recent_activities
        }
        return dashboard_data
# ==================== Users Class Ends Here ====================


# ==================== Admins Class ====================
class Admins(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    admin_name = db.Column("admin_name", db.String(50), nullable=False)
    admin_gender = db.Column("admin_gender", db.String(8), nullable=False)
    admin_email = db.Column("admin_email", db.String(50), nullable=True)
    admin_phno = db.Column("admin_phno", db.String(12), nullable=False)
    admin_id = db.Column("admin_id", db.String(20), nullable=False)
    admin_password = db.Column("admin_password", db.String(20), nullable=False)

    @staticmethod
    def validate_admin(entered_username, entered_password):  # return true if admin exist in database
        admin = Admins.query.filter_by(admin_id=entered_username).first()
        if admin:
            if admin.admin_password == entered_password:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def get_admin_data(admin_id):
        admin_data = Admins.query.filter_by(admin_id=admin_id).first()
        return admin_data

    @staticmethod
    def get_all_admins_data():
        admins = Admins.query.all()
        return admins

    @staticmethod
    def update_admin_data(password, name, phno, gender, email):
        if session["user_type"] == "admin":
            admin_data = Admins.get_admin_data(session["user"])
            admin_data.admin_password = password
            admin_data.admin_name = name
            admin_data.admin_phno = phno
            admin_data.admin_gender = gender
            admin_data.admin_email = email
            db.session.commit()
            return True
        else:
            return False

    @staticmethod
    def generate_admin_dashboard_data():
        total_stores = Stores.query.count()
        active_stores = Stores.query.filter_by(store_status="Working").count()
        unactive_stores = Stores.query.filter_by(store_status="Closed").count()
        total_brands = Brands.query.count()
        active_brands = Brands.query.filter_by(brand_status="Active").count()
        unactive_brands = Brands.query.filter_by(brand_status="UnActive").count()
        all_users = Users.query.count()
        active_users = Users.query.filter_by(user_status="Active").count()
        unactive_user = Users.query.filter_by(user_status="UnActive").count()
        total_messages = Messages.query.filter_by(message_to=session["user"]).count()
        unread_messages = Messages.query.filter_by(message_to=session["user"]).filter_by(status="UnRead").count()
        readed_messages = Messages.query.filter_by(message_to=session["user"]).filter_by(status="Readed").count()
        total_products = Products.query.count()
        out_of_order_prod = Products.query.filter(Products.qty_remain <= 0).count()
        near_to_out_of_order_prod = Products.query.filter(Products.qty_remain >= 1).filter(Products.qty_remain <= 20)\
            .count()
        total_members = Members.query.count()
        members_data = Members.get_all_members_data()
        total_member_profit = 0
        total_discount_given = 0
        for data in members_data:
            total_member_profit = int(total_member_profit) + int(data.gen_profit)
            total_discount_given = int(total_discount_given) + int(data.discount_given)
        last_ten_days_selling = SellingByDate.query.order_by(desc(SellingByDate.sno)).limit(10)
        total_inventory_selling = SellingByDate.query.order_by(desc(SellingByDate.sno)).all()
        next_10_days_forecast = ForecastData.query.filter(ForecastData.date > str(date.today())).\
            filter(ForecastData.date <= str(date.today() + timedelta(10))).all()

        dashboard_data = {
            "total_stores": total_stores,
            "active_stores": active_stores,
            "unactive_stores": unactive_stores,
            "total_brands": total_brands,
            "active_brands": active_brands,
            "unactive_brands": unactive_brands,
            "all_users": all_users,
            "active_users": active_users,
            "unactive_users": unactive_user,
            "total_messages": total_messages,
            "unread_messages": unread_messages,
            "readed_messages": readed_messages,
            "total_prod": total_products,
            "out_of_order_prod": out_of_order_prod,
            "near_to_out_of_order_prod": near_to_out_of_order_prod,
            "total_members": total_members,
            "total_member_profit": total_member_profit,
            "total_discount_given": total_discount_given,
            "last_10_days_selling": last_ten_days_selling,
            "total_inventory_selling": total_inventory_selling,
            "next_days_forecast": next_10_days_forecast
        }

        return dashboard_data
# ==================== Admins Class Ends Here ====================


# =============================== Stores Class ===============================
class Stores(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    store_id = db.Column("store_id", db.String(5), nullable=False)
    store_location = db.Column("store_location", db.String(30), nullable=False)
    store_status = db.Column("store_status", db.String(10), nullable=False)
    store_gen_rev = db.Column("store_gen_rev", db.Integer, nullable=True)
    store_gen_profit = db.Column("store_gen_profit", db.Integer, nullable=True)
    store_total_sold = db.Column("store_total_sold", db.Integer, nullable=True)

    @staticmethod
    def get_all_stores_data():
        stores_data = Stores.query.all()
        return stores_data

    @staticmethod
    def get_store_data(store_id):
        store_data = Stores.query.filter_by(store_id=store_id).first()
        return store_data

    @staticmethod
    def save_new_store(store_id, store_location, store_status):
        if Stores.get_store_data(store_id):
            return False  # checking for id redundancy
        else:
            save_store_query = Stores(store_id=store_id, store_location=store_location, store_status=store_status,
                                      store_gen_rev=0, store_gen_profit=0, store_total_sold=0)
            db.session.add(save_store_query)  # running the query
            db.session.commit()  # saving data
            return True

    @staticmethod
    def delete_this_store(store_id):
        store_to_delete = Stores.get_store_data(store_id)
        db.session.delete(store_to_delete)
        db.session.commit()
        users_of_store = Users.query.filter_by(working_store_id=store_id).all()
        for user in users_of_store:
            user.working_store_id = ""
            user.user_status = "UnActive"
        db.session.commit()
        store_details = StoreByDateDetails.query.filter_by(store_id=store_id).all()
        for store in store_details:
            db.session.delete(store)
        db.session.commit()
        return True

    @staticmethod
    def update_store_data(old_store_id, new_store_id, store_status, store_location):
        store_data = Stores.get_store_data(old_store_id)
        if store_data:
            if old_store_id != new_store_id:
                check = Stores.get_store_data(new_store_id)
                if check:
                    return False
            # Updating Simple Store Records
            store_data.store_status = store_status
            store_data.store_location = store_location
            store_data.store_id = new_store_id
            db.session.commit()
            # Now Updating Previous Records For Selling
            store_data_date = StoreByDateDetails.get_all_store_data_by_date(old_store_id)
            if store_data_date:
                for data in store_data_date:
                    print(data.store_id)
                    data.store_id = new_store_id
                db.session.commit()

            # Updating User Working Stores
            user_store = Users.get_all_user_data()
            if user_store:
                for user in user_store:
                    if user.working_store_id == old_store_id:
                        user.working_store_id = new_store_id
                db.session.commit()

            # Return True if all goes well
            return True
        else:
            return False
# =============================== Stores Class Ends Here ===============================


# =============================== StoresByDate Class  ===============================
class StoreByDateDetails(db.Model):  # Table save data on date basis
    sno = db.Column("sno", db.Integer, primary_key=True)
    store_id = db.Column("store_id", db.String(5), nullable=False)
    date = db.Column("date", db.Date, nullable=False)
    gen_rev = db.Column("gen_rev", db.Integer, nullable=True)
    gen_profit = db.Column("gen_profit", db.Integer, nullable=True)
    total_sold = db.Column("total_sold", db.Integer, nullable=True)

    @staticmethod
    def get_all_store_data_by_date(store_id):
        all_store_data_by_date = StoreByDateDetails.query.filter_by(store_id=store_id).\
            order_by(desc(StoreByDateDetails.date)).all()
        return all_store_data_by_date

    @staticmethod
    def get_for_report_data(from_date, to_date, store):
        report_data = StoreByDateDetails.query.filter_by(store_id=store).filter(StoreByDateDetails.date >= from_date).\
            filter(StoreByDateDetails.date <= to_date).all()
        return report_data
# =============================== StoresByDate Class Ends Here  ===============================


# =============================== Brands Class  ===============================
class Brands(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    brand_id = db.Column("brand_id", db.String(5), nullable=False)
    brand_name = db.Column("brand_name", db.String(35), nullable=False)
    brand_status = db.Column("brand_status", db.Text, nullable=False)
    brand_img_url = db.Column("brand_img_url", db.String(60), nullable=True)

    @staticmethod
    def get_all_brands():
        all_brands = Brands.query.all()
        return all_brands

    @staticmethod
    def get_active_brands():
        all_brands = Brands.query.filter_by(brand_status="Active").all()
        return all_brands

    @staticmethod
    def get_this_brand(brand_id):
        brand_data = Brands.query.filter_by(brand_id=brand_id).first()
        return brand_data

    @staticmethod
    def save_new_brand(brand_id, status, name, img_url):
        if Brands.get_this_brand(brand_id):
            return False
        else:
            brand_save_query = Brands(brand_id=brand_id, brand_name=name, brand_status=status, brand_img_url=img_url)
            db.session.add(brand_save_query)
            db.session.commit()
            return True

    @staticmethod
    def delete_this_brand(brand_id):
        brand_to_delete = Brands.get_this_brand(brand_id)
        if brand_to_delete.brand_img_url:
            remove(app.config["IMG_UPLOAD_FOLDER"] + "/" + brand_to_delete.brand_img_url)
        brand_prods = Products.get_brand_prod(brand_to_delete.brand_name)
        for prod in brand_prods:
            prod.prod_brand = ""
        db.session.commit()
        db.session.delete(brand_to_delete)
        db.session.commit()
        return True

    @staticmethod
    def update_brand_data(old_brand_id, new_brand_id, status, name, img_url):
        brand_data = Brands.get_this_brand(old_brand_id)
        if old_brand_id != new_brand_id:
            check = Brands.get_this_brand(new_brand_id)
            if check:
                return False
        if brand_data:
            all_prods = Products.get_all_products()
            for prod in all_prods:
                if prod.prod_brand == brand_data.brand_name:
                    prod.prod_brand = name
            db.session.commit()
            # Updating Simple Brands Records
            brand_data.brand_id = new_brand_id
            brand_data.brand_status = status
            brand_data.brand_name = name
            if img_url:
                remove(app.config["IMG_UPLOAD_FOLDER"] + "/" + brand_data.brand_img_url)
                brand_data.brand_img_url = img_url
            db.session.commit()
            return True
        else:
            return False

    @staticmethod
    def get_brand_prod_details(brand_id):
        brand_data = Brands.get_this_brand(brand_id)
        brand_prods = Products.get_brand_prod(brand_data.brand_name)
        return brand_prods
# =============================== Brands Class Ends Here ===============================


# =============================== Products Class ===============================
class Products(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    prod_id = db.Column("prod_id", db.String(10), nullable=False)
    prod_name = db.Column("prod_name", db.String(60), nullable=False)
    prod_color = db.Column("prod_color", db.String(20), nullable=True)
    prod_pic_url = db.Column("prod_pic_url", db.String(60), nullable=True)
    prod_location = db.Column("prod_location", db.String(15), nullable=False)
    buy_price = db.Column("buy_price", db.Integer, nullable=False)
    sell_price = db.Column("sell_price", db.Integer, nullable=False)
    qty_total = db.Column("qty_total", db.Integer, nullable=False)
    qty_remain = db.Column("qty_remain", db.Integer, nullable=False)
    description = db.Column("description", db.String(200), nullable=True)
    prod_brand = db.Column("prod_brand", db.Text, nullable=True)
    discount_price = db.Column("discount_price", db.Integer, nullable=True)

    @staticmethod
    def get_all_products():
        all_products = Products.query.all()
        return all_products

    @staticmethod
    def get_prod_for_sale():
        all_products = Products.get_all_products()
        all_brands = Brands.get_all_brands()
        active_brands = list()
        for brand in all_brands:
            if brand.brand_status == "Active":
                active_brands.append(brand.brand_name)
        products_to_sell = list()
        for prod in all_products:
            if prod.prod_brand in active_brands:
                if prod.qty_remain > 0:
                    products_to_sell.append(prod.prod_name)
        return products_to_sell

    @staticmethod
    def get_brand_prod(brand_name):
        brand_prod = Products.query.filter_by(prod_brand=brand_name).all()
        return brand_prod

    @staticmethod
    def count_brand_products(brand_name):
        no_of_products = Products.query.filter_by(prod_brand=brand_name).all()
        return len(no_of_products)

    @staticmethod
    def get_this_product(prod_id):
        product_data = Products.query.filter_by(prod_id=prod_id).first()
        return product_data

    @staticmethod
    def get_prod_by_name(prod_name):
        prod = Products.query.filter_by(prod_name=prod_name).first()
        return prod

    @staticmethod
    def save_new_product(prod_id, loc, name, brand, buy_price, sell_price, qty_total, dis_price, color,
                         description, pic_url):
        if Products.get_this_product(prod_id):
            return False
        elif Products.get_prod_by_name(name):
            return False
        else:
            save_query = Products(prod_id=prod_id, prod_name=name, prod_color=color, prod_pic_url=pic_url,
                                  prod_location=loc, buy_price=buy_price, sell_price=sell_price, qty_total=qty_total,
                                  qty_remain=qty_total, description=description, prod_brand=brand,
                                  discount_price=dis_price)
            db.session.add(save_query)
            db.session.commit()
            save_query2 = ProductsDetails(prod_id=prod_id, prod_total_sold=0, prod_gen_rev=0, prod_gen_profit=0)
            db.session.add(save_query2)
            db.session.commit()
            return True

    @staticmethod
    def delete_this_product(prod_id):
        prod_to_delete = Products.get_this_product(prod_id)
        if prod_to_delete.prod_pic_url:
            remove(app.config["IMG_UPLOAD_FOLDER"] + "/" + prod_to_delete.prod_pic_url)
        db.session.delete(prod_to_delete)
        db.session.commit()
        prod_to_delete = ProductsDetails.get_prod_details(prod_id)
        db.session.delete(prod_to_delete)
        db.session.commit()
        if ProdSalesByDate.delete_prod_sales_details(prod_id):
            return True
        else:
            return False

    @staticmethod
    def update_product(old_prod_id, new_prod_id, loc, name, brand, buy_price, sell_price, qty_total,
                       discount_price, color, img_url):
        prod_to_update = Products.get_this_product(old_prod_id)
        if prod_to_update:
            if old_prod_id != new_prod_id:
                check = Products.get_this_product(new_prod_id)
                if check:
                    return False
            prod_to_update.prod_id = new_prod_id
            prod_to_update.prod_name = name
            prod_to_update.prod_location = loc
            prod_to_update.prod_color = color
            prod_to_update.buy_price = buy_price
            prod_to_update.sell_price = sell_price
            if int(sell_price) < int(buy_price):
                return False
            if int(prod_to_update.qty_total) > int(qty_total):
                return False
            prod_to_update.qty_remain = prod_to_update.qty_remain + (int(qty_total) - int(prod_to_update.qty_total))
            prod_to_update.qty_total = qty_total
            prod_to_update.prod_brand = brand
            if int(discount_price) > int(prod_to_update.sell_price) - int(prod_to_update.buy_price):
                return False
            prod_to_update.discount_price = discount_price
            if img_url:
                prod_to_update.prod_pic_url = img_url
            db.session.commit()
            # Updating Product Details Table
            prod_detail = ProductsDetails.get_prod_details(old_prod_id)
            if prod_detail:
                prod_detail.prod_id = new_prod_id
                db.session.commit()
            # Update Prod Sales By Date
            prod_by_date = ProdSalesByDate.get_prod_by_date_sales(old_prod_id)
            if prod_by_date:
                for prod in prod_by_date:
                    prod.prod_id = new_prod_id
                db.session.commit()
            return True
        else:
            return False
# =============================== Products Class Ends Here ===============================


# =============================== ProductDetails Class ===============================
class ProductsDetails(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    prod_id = db.Column("prod_id", db.Integer, nullable=False)
    prod_total_sold = db.Column("prod_total_sold", db.Integer, nullable=False)
    prod_gen_rev = db.Column("prod_gen_rev", db.Integer, nullable=False)
    prod_gen_profit = db.Column("prod_gen_profit", db.Integer, nullable=False)

    @staticmethod
    def get_prod_details(prod_id):
        prod_details = ProductsDetails.query.filter_by(prod_id=prod_id).first()
        return prod_details
# =============================== ProductDetails Class Ends Here ===============================


# =============================== SellingByDate Class ===============================
class SellingByDate(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    date = db.Column("date", db.String(15), nullable=False)
    total_sold = db.Column("total_sold", db.Integer, nullable=False)
    gen_rev = db.Column("gen_rev", db.Integer, nullable=False)
    gen_profit = db.Column("gen_profit", db.Integer, nullable=False)

    @staticmethod
    def add_sales_by_date(total_sold, rev, profit):
        today = date.today()
        check = SellingByDate.query.filter_by(date=today).first()
        if check:
            check.total_sold = int(check.total_sold) + int(total_sold)
            check.gen_rev = int(check.gen_rev) + int(rev)
            check.gen_profit = int(check.gen_profit) + int(profit)
            db.session.commit()
            if TopProducts.save_previous_day_top_prod(1):
                return True
            else:
                return False
        else:
            query = SellingByDate(date=today, total_sold=total_sold, gen_rev=rev, gen_profit=profit)
            db.session.add(query)
            db.session.commit()
            if TopProducts.save_previous_day_top_prod(1):
                return True
            else:
                return False

    @staticmethod
    def get_sell_records_by_date():
        data = SellingByDate.query.all()
        return data

    @staticmethod
    def get_min_max_sold():
        max_sold = SellingByDate.query.filter(SellingByDate.total_sold).order_by(desc(SellingByDate.total_sold)).\
            first()
        min_sold = SellingByDate.query.filter(SellingByDate.total_sold).order_by(asc(SellingByDate.total_sold)).\
            first()
        return max_sold, min_sold
# =============================== SellingByDate Class Ends Here ============================


# =============================== ProdSalesByDate Class ============================
class ProdSalesByDate(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    prod_id = db.Column("prod_id", db.String(10), nullable=False)
    date = db.Column("date", db.String(15), nullable=False)
    total_sold = db.Column("total_sold", db.Integer, nullable=False)
    gen_rev = db.Column("gen_rev", db.Integer, nullable=False)
    gen_profit = db.Column("gen_profit", db.Integer, nullable=False)
    store = db.Column("store", db.String(5), nullable=False)

    @staticmethod
    def save_prod_by_date_sales(prod_id, sold, rev, profit):
        today = date.today()
        check = ProdSalesByDate.query.filter_by(prod_id=prod_id, date=today).first()
        if check:
            check.total_sold = int(check.total_sold) + int(sold)
            check.gen_rev = int(check.gen_rev) + int(rev)
            check.gen_profit = int(check.gen_rev) + int(profit)
            db.session.commit()
            return True
        else:
            user = Users.get_user_data(session["user"])
            query = ProdSalesByDate(date=today, total_sold=sold, gen_rev=rev, gen_profit=profit,
                                    store=user.working_store_id)
            db.session.add(query)
            db.session.commit()
            return True

    @staticmethod
    def delete_prod_sales_details(prod_id):
        data_to_delete = ProductsDetails.query.filter_by(prod_id=prod_id).all()
        for data in data_to_delete:
            db.session.delete(data)
        db.session.commit()
        return True

    @staticmethod
    def get_prod_by_date_sales(prod_id):
        prod_by_date = ProdSalesByDate.query.filter_by(prod_id=prod_id).order_by(desc(ProdSalesByDate.date)).all()
        return prod_by_date

    @staticmethod
    def get_for_report_data(from_date, to_date, product):
        report_data = ProdSalesByDate.query.filter_by(prod_id=product).filter(ProdSalesByDate.date >= from_date).\
            filter(ProdSalesByDate.date <= to_date).all()
        return report_data
# =============================== ProdSalesByDate Class Ends Here ============================


# =============================== NonMembersData Class ============================
class NonMembersData(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    buyer_name = db.Column("buyer_name", db.Text, nullable=False)
    location = db.Column("location", db.String(120), nullable=True)
    phno = db.Column("ph_no", db.String(15), nullable=False)
    prod_name = db.Column("prod_name", db.String(50), nullable=False)
    qty = db.Column("qty", db.Integer, nullable=False)
    date = db.Column("date", db.String(20), nullable=False)
    paid_amount = db.Column("paid_amount", db.Integer, nullable=False)

    @staticmethod
    def save_non_member_data(buyer, loc, phno, prod_name, qty, date_now, amount):
        query = NonMembersData(buyer_name=buyer, location=loc, phno=phno, prod_name=prod_name, qty=qty,
                               date=date_now, paid_amount=amount)
        db.session.add(query)
        db.session.commit()

    @staticmethod
    def prod_selling_process(buyer, loc, phno, prod_name, qty):
        date_now = datetime.now()
        date_now = date_now.strftime("%d/%m/%Y %H:%M:%S")
        prod_data = Products.get_prod_by_name(prod_name)
        if str(prod_data.prod_name) == str(prod_name):
            # Now updating Product Quantity ************
            qty_remain = int(prod_data.qty_remain) - int(qty)
            if qty_remain < 0:
                return False
            else:
                prod_data.qty_remain = int(prod_data.qty_remain) - int(qty)
                db.session.commit()
            paid_amount = int(prod_data.sell_price) * int(qty)
            profit = (int(prod_data.sell_price) - int(prod_data.buy_price)) * int(qty)
            # ====== Saving Non Member Data =====
            NonMembersData.save_non_member_data(buyer, loc, phno, prod_name, qty, date_now, paid_amount)
            # ====== Saving Non Member Data =====
            Invoices.save_invoice(buyer, "Simple", date_now, prod_name, qty, paid_amount, session["user"])
            if sell_the_product(prod_data, qty, paid_amount, profit):
                return True
            else:
                return False
        else:
            return False
# =============================== NonMembersData Class Ends Here ============================


# =============================== Members Class ============================
class Members(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    member_id = db.Column("member_id", db.String(10), nullable=True)
    member_name = db.Column("member_name", db.Text, nullable=False)
    member_phno = db.Column("member_phno", db.String(12), nullable=False)
    member_email = db.Column("member_email", db.String(60), nullable=True)
    member_address = db.Column("member_address", db.String(120), nullable=False)
    total_buy = db.Column("total_buy", db.Integer, nullable=False)
    gen_rev = db.Column("gen_rev", db.Integer, nullable=False)
    gen_profit = db.Column("gen_profit", db.Integer, nullable=False)
    discount_given = db.Column("discount_given", db.Integer, nullable=False)
    date_of_membership = db.Column("date_of_membership", db.String(20), nullable=False)

    @staticmethod
    def save_new_member(member_id, name, phno, email, address):
        simple_date = date.today()
        if Members.get_this_members_data(member_id):
            return False
        check = Members.query.filter_by(member_name=name).first()
        if check:
            return False
        else:
            query = Members(member_id=member_id, member_name=name, member_phno=phno, member_email=email,
                            member_address=address, total_buy=0, gen_rev=0, gen_profit=0, discount_given=0,
                            date_of_membership=simple_date)
            db.session.add(query)
            db.session.commit()
            return True

    @staticmethod
    def get_all_members_data():
        members_data = Members.query.all()
        return members_data

    @staticmethod
    def get_member_data_by_name(member_name):
        member_data = Members.query.filter_by(member_name=member_name).first()
        return member_data

    @staticmethod
    def get_this_members_data(member_id):
        member_data = Members.query.filter_by(member_id=member_id).first()
        return member_data

    @staticmethod
    def delete_this_member(member_id):
        member_to_delete = Members.get_this_members_data(member_id)
        db.session.delete(member_to_delete)
        db.session.commit()
        if MembersSalesDetail.delete_member_sales_data(member_id):
            return True
        else:
            return False

    @staticmethod
    def update_member(old_member_id, new_id, name, email, phno, address):
        member_data = Members.get_this_members_data(old_member_id)
        if member_data:
            if old_member_id != new_id:
                check = Members.get_this_members_data(new_id)
                if check:
                    return False
            else:
                member_data.member_id = new_id
                member_data.member_name = name
                member_data.member_email = email
                member_data.member_phno = phno
                member_data.member_address = address
                db.session.commit()
                return True
        else:
            return False
# =============================== Members Class Ends Here ============================


# =============================== MembersSalesDetail Class ===================
class MembersSalesDetail(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    member_id = db.Column("member_id", db.String(10), nullable=True)
    prod_name = db.Column("prod_name", db.String(60), nullable=False)
    date = db.Column("date", db.String(20), nullable=False)
    qty = db.Column("qty", db.Integer, nullable=False)
    paid_amount = db.Column("paid_amount", db.Integer, nullable=False)

    @staticmethod
    def get_member_sales_data(member_id):
        member_sales_data = MembersSalesDetail.query.filter_by(member_id=member_id).all()
        return member_sales_data

    @staticmethod
    def delete_member_sales_data(member_id):
        data_to_delete = MembersSalesDetail.query.filter_by(member_id=member_id).all()
        for data in data_to_delete:
            db.session.delete(data)
        db.session.commit()
        return True

    @staticmethod
    def save_member_sales(member_id, prod_name, date_now, qty, amount):
        query = MembersSalesDetail(member_id=member_id, prod_name=prod_name, date=date_now,
                                   qty=qty, paid_amount=amount)
        db.session.add(query)
        db.session.commit()

    @staticmethod
    def prod_selling_process(member_name, prod_name, qty):
        date_now = datetime.now()
        date_now = date_now.strftime("%d/%m/%Y %H:%M:%S")
        prod_data = Products.get_prod_by_name(prod_name)
        if str(prod_data.prod_name) == str(prod_name):
            # Now updating Product Quantity ************
            qty_remain = int(prod_data.qty_remain) - int(qty)
            if qty_remain < 0:
                return False
            else:
                prod_data.qty_remain = int(prod_data.qty_remain) - int(qty)
                db.session.commit()
            paid_amount = (int(prod_data.sell_price) * int(qty)) - (int(prod_data.discount_price) * int(qty))
            profit = ((int(prod_data.sell_price) - int(prod_data.buy_price)) * int(qty)) - \
                     (int(prod_data.discount_price) * int(qty))
            # Save Member Sales Data
            member_data = Members.get_member_data_by_name(member_name)
            # Now Update Member Data
            member_data.total_buy = int(member_data.total_buy) + int(qty)
            member_data.gen_rev = int(member_data.gen_rev) + int(paid_amount)
            member_data.gen_profit = int(member_data.gen_profit) + int(profit)
            member_data.discount_given = int(prod_data.discount_price) * int(qty)
            db.session.commit()
            MembersSalesDetail.save_member_sales(member_data.member_id, prod_name, date_now, qty, paid_amount)
            Invoices.save_invoice(member_name, "Member", date_now, prod_name, qty, paid_amount, session["user"])
            if sell_the_product(prod_data, qty, paid_amount, profit):
                return True
            else:
                return False
        else:
            return False
# =============================== MembersSalesDetail Class Ends Here ============================


# *************** This function is written to implement DRY principle *************** (No Class Function)
def sell_the_product(prod_data, qty, paid_amount, profit):
    simple_date = date.today()
    prod_details = ProductsDetails.query.filter_by(prod_id=prod_data.prod_id).first()
    if prod_details:
        prod_details.prod_total_sold = int(prod_details.prod_total_sold) + int(qty)
        prod_details.prod_gen_rev = int(prod_details.prod_gen_rev) + int(paid_amount)
        prod_details.prod_gen_profit = int(prod_details.prod_gen_profit) + int(profit)
        db.session.commit()
    else:
        query1 = ProductsDetails(prod_id=prod_data.prod_id, prod_total_sold=qty, prod_gen_rev=paid_amount,
                                 prod_gen_profit=profit)
        db.session.add(query1)
        db.session.commit()
    # Now By Date prod Data Updating **************
    prod_by_date_data = ProdSalesByDate.query.filter_by(prod_id=prod_data.prod_id, date=simple_date).first()
    if prod_by_date_data:
        prod_by_date_data.total_sold = int(prod_by_date_data.total_sold) + int(qty)
        prod_by_date_data.gen_rev = int(prod_by_date_data.gen_rev) + int(paid_amount)
        prod_by_date_data.gen_profit = int(prod_by_date_data.gen_profit) + int(profit)
        db.session.commit()
    else:
        user = Users.get_user_data(session["user"])

        query2 = ProdSalesByDate(prod_id=prod_data.prod_id, date=simple_date, total_sold=qty,
                                 gen_rev=paid_amount, gen_profit=profit, store=user.working_store_id)
        db.session.add(query2)
        db.session.commit()
    # Now By Date overall Data Updating **************
    check = SellingByDate.add_sales_by_date(qty, paid_amount, profit)
    if check is False:
        return False
    # Now Store By Date data update ************
    user = Users.query.filter_by(user_id=session["user"]).first()
    user_store = user.working_store_id
    store_by_date = StoreByDateDetails.query.filter_by(store_id=user_store, date=simple_date).first()
    if store_by_date:
        store_by_date.gen_rev = int(store_by_date.gen_rev) + int(paid_amount)
        store_by_date.gen_profit = int(store_by_date.gen_profit) + int(profit)
        store_by_date.total_sold = int(store_by_date.total_sold) + int(qty)
        db.session.commit()
    else:
        query4 = StoreByDateDetails(store_id=user_store, date=simple_date, gen_rev=paid_amount,
                                    gen_profit=profit, total_sold=qty)
        db.session.add(query4)
        db.session.commit()
    # now update store data
    store_data = Stores.query.filter_by(store_id=user_store).first()
    store_data.store_gen_rev = int(store_data.store_gen_rev) + int(paid_amount)
    store_data.store_gen_profit = int(store_data.store_gen_profit) + int(profit)
    store_data.store_total_sold = int(store_data.store_total_sold) + int(qty)
    db.session.commit()
    forecast_data = ForecastData.get_this_forecast_data(simple_date)
    if forecast_data:
        forecast_data.actual_sold = int(forecast_data.actual_sold) + int(qty)
        forecast_data.actual_profit = int(forecast_data.actual_profit) + int(profit)
        db.session.commit()
    return True
# *************** This Above function Ends Here *************** (No Class Function)


# ========================== Invoices Class ==================================
class Invoices(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    buyer = db.Column("buyer", db.String(50), nullable=False)
    buyer_type = db.Column("buyer_type", db.String(12), nullable=False)
    date = db.Column("date", db.String(25), nullable=False)
    prod_name = db.Column("prod_name", db.String(50), nullable=False)
    qty = db.Column("qty", db.Integer, nullable=False)
    paid_amount = db.Column("paid_amount", db.Integer, nullable=False)
    prod_sold_by = db.Column("prod_sold_by", db.String(50), nullable=False)

    @staticmethod
    def save_invoice(buyer, buyer_type, date_now, prod_name, qty, paid_amount, sold_by):
        query = Invoices(buyer=buyer, buyer_type=buyer_type, date=date_now, prod_name=prod_name, qty=qty,
                         paid_amount=paid_amount, prod_sold_by=sold_by)
        db.session.add(query)
        db.session.commit()

    @staticmethod
    def get_recent_invoice():
        invoice = Invoices.query.order_by(desc(Invoices.sno)).first()
        return invoice

    @staticmethod
    def get_recent_invoice_after_check():
        invoice = Invoices.query.filter_by(prod_sold_by=session["user"]).order_by(desc(Invoices.sno)).first()
        return invoice

    @staticmethod
    def get_this_invoice(sno):
        invoice = Invoices.query.filter_by(sno=sno).first()
        return invoice

    @staticmethod
    def get_all_invoices():
        all_invoices = Invoices.query.order_by(desc(Invoices.sno)).all()
        return all_invoices

    @staticmethod
    def get_this_user_invoices(user):
        all_invoices = Invoices.query.filter_by(prod_sold_by=user).order_by(desc(Invoices.sno)).all()
        return all_invoices

    @staticmethod
    def get_invoice_for_user_after_check(sno):
        invoice = Invoices.query.filter_by(sno=sno).first()
        if invoice.prod_sold_by == session["user"]:
            return invoice
        else:
            return False
# ========================== Invoices Class Ends Here ==================================


# ========================== Messages Class ==================================
class Messages(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    message_from = db.Column("message_from", db.String(35), nullable=False)
    message_to = db.Column("message_to", db.String(35), nullable=False)
    sender_type = db.Column("sender_type", db.String(8), nullable=False)
    message_id = db.Column("message_id", db.String(25), nullable=False)
    subject = db.Column("subject", db.String(30), nullable=False)
    body = db.Column("body", db.String(160), nullable=False)
    send_date = db.Column("send_date", db.String(16), nullable=False)
    status = db.Column("status", db.String(6), nullable=False)

    @staticmethod
    def send_new_message(m_from, m_to, subject, body):
        send_date = datetime.now()
        send_date = send_date.strftime("%d/%m/%Y %H:%M:%S")
        m_id = str(random.randint(1, 5000)) + "-" + str(subject[:5]) + "-" + str(m_to)
        send_message_query = Messages(message_from=m_from, message_to=m_to, sender_type=session["user_type"],
                                      message_id=m_id, subject=subject, body=body, send_date=send_date, status="UnRead")
        db.session.add(send_message_query)
        db.session.commit()
        return True

    @staticmethod
    def get_messages_for(message_to):
        messages = Messages.query.filter_by(message_to=message_to).order_by(desc(Messages.sno)).all()
        return messages

    @staticmethod
    def get_send_messages(message_from):
        messages = Messages.query.filter_by(message_from=message_from).order_by(desc(Messages.sno)).all()
        return messages

    @staticmethod
    def get_message(message_id):
        message = Messages.query.filter_by(message_id=message_id).first()
        return message

    @staticmethod
    def delete_message(message_id):
        message_to_delete = Messages.get_message(message_id)
        if message_to_delete:
            db.session.delete(message_to_delete)
            db.session.commit()
            return True
        else:
            return False

    @staticmethod
    def update_message_status(message_id):
        message = Messages.get_message(message_id)
        if message:
            message.status = "Readed"
            db.session.commit()
# ========================== Messages Class Ends Here ==================================


# ========================== ReportsDraft Class ==================================
class ReportsDraft(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    gen_by = db.Column("gen_by", db.String(35), nullable=False)
    gen_on = db.Column("gen_on", db.String(25), nullable=False)
    report_of_date = db.Column("report_of_date", db.String(30), nullable=False)
    report_of = db.Column("report_of", db.String(50), nullable=False)
    type_of = db.Column("type_of", db.String(20), nullable=False)

    @staticmethod
    def get_report_data_from_draft(sno):
        report_data = ReportsDraft.query.filter_by(sno=sno).first()
        return report_data

    @staticmethod
    def generate_this_report(sno_of_report):
        report = ReportsDraft.query.filter_by(sno=sno_of_report).first()
        if report.type_of == "Store":
            report = ReportsDraft.generate_store_report(report.report_of_date[:10], report.report_of_date[11:],
                                                        report.report_of)
            if report:
                return report
            else:
                return False
        elif report.type_of == "Product":
            report = ReportsDraft.generate_product_report(report.report_of_date[:10], report.report_of_date[11:],
                                                          report.report_of)
            if report:
                return report
            else:
                return False
        else:
            pass

    @staticmethod
    def get_last_report_sno():
        report = ReportsDraft.query.order_by(desc(ReportsDraft.sno)).first()
        return report.sno

    @staticmethod
    def get_reports_by(gen_by):
        all_reports = ReportsDraft.query.filter_by(gen_by=gen_by).all()
        return all_reports

    @staticmethod
    def save_report_to_draft(from_date, to_date, gen_by, report_of, type_of):
        gen_on = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        report_of_date = str(from_date) + "-" + str(to_date)
        save_report = ReportsDraft(gen_by=gen_by, gen_on=gen_on, report_of_date=report_of_date, report_of=report_of,
                                   type_of=type_of)
        db.session.add(save_report)
        db.session.commit()
        return True

    @staticmethod
    def check_dates_for_reports(from_date, to_date):
        # please do not try to understand, this code is just to check that 'from' date is not greater then 'to' date
        if int(from_date[8:]) > int(to_date[8:]):
            if int(from_date[5:7]) > int(to_date[5:7]):
                if int(from_date[:4]) > int(to_date[:4]):
                    return False
        if int(from_date[5:7]) > int(to_date[5:7]):
            if int(from_date[:4]) > int(to_date[:4]):
                return False
        if int(from_date[:4]) > int(to_date[:4]):
            return False

        return True

    @staticmethod
    def generate_store_report(from_date, to_date, store):
        if ReportsDraft.check_dates_for_reports(from_date, to_date):
            report_data = StoreByDateDetails.get_for_report_data(from_date, to_date, store)
            report = {
                "total_rev": 0,
                "total_profit": 0,
                "total_sold": 0
            }
            for data in report_data:
                report["total_rev"] = report["total_rev"] + int(data.gen_rev)
                report["total_profit"] = report["total_profit"] + int(data.gen_profit)
                report["total_sold"] = report["total_sold"] + int(data.total_sold)

            return report
        else:
            return False

    @staticmethod
    def generate_product_report(from_date, to_date, product):
        if ReportsDraft.check_dates_for_reports(from_date, to_date):
            report_data = ProdSalesByDate.get_for_report_data(from_date, to_date, product)
            report = {
                "total_rev": 0,
                "total_profit": 0,
                "total_sold": 0
            }
            for data in report_data:
                report["total_rev"] = report["total_rev"] + int(data.gen_rev)
                report["total_profit"] = report["total_profit"] + int(data.gen_profit)
                report["total_sold"] = report["total_sold"] + int(data.total_sold)

            return report
        else:
            return False

    @staticmethod
    def delete_this_report(sno):
        report = ReportsDraft.get_report_data_from_draft(sno)
        if report.gen_by == session["user"]:
            db.session.delete(report)
            db.session.commit()
            return True
        else:
            return False
# ========================== ReportsDraft Class Ends Here ==================================


# ========================== ForecastData Class ==================================
class ForecastData(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True)
    date = db.Column("date", db.String(25), nullable=False)
    sold = db.Column("sold", db.Integer, nullable=False)
    profit = db.Column("profit", db.Integer, nullable=False)
    actual_sold = db.Column("actual_sold", db.Integer, nullable=False)
    actual_profit = db.Column("actual_profit", db.Integer, nullable=False)

    @staticmethod
    def save_next_forecast(forecast_sold, forecast_profit):
        forecast_data = ForecastData.get_by_date_forecast()
        if forecast_data:
            if len(forecast_data) != 15:
                data_length = len(forecast_data)
                to_save = 15 - len(forecast_data)
                j = 0
                k = 1
                for _ in range(to_save):
                    save_query = ForecastData(date=str(date.today()+timedelta(data_length+k)),
                                              sold=forecast_sold[data_length+j], profit=forecast_profit[data_length+j],
                                              actual_sold=0, actual_profit=0)
                    db.session.add(save_query)
                    db.session.commit()
                    j += 1
                    k += 1
                # update previous data
                i = 0
                for data in forecast_data:
                    data.sold = forecast_sold[i]
                    data.profit = forecast_profit[i]
                    i += 1
                    db.session.commit()
            else:
                i = 0
                for data in forecast_data:
                    data.sold = forecast_sold[i]
                    data.profit = forecast_profit[i]
                    i += 1
                    db.session.commit()
        else:
            j = 0
            k = 1
            for _ in range(15):
                save_query = ForecastData(date=str(date.today() + timedelta(k)),
                                          sold=forecast_sold[j], profit=forecast_profit[j], actual_sold=0,
                                          actual_profit=0)
                db.session.add(save_query)
                db.session.commit()
                j += 1
                k += 1

    @staticmethod
    def get_by_date_forecast():
        from_date = date.today() + timedelta(1)
        to_date = date.today() + timedelta(15)
        next_15_days_forecast = ForecastData.query.filter(ForecastData.date >= from_date).\
            filter(ForecastData.date <= to_date).all()
        return next_15_days_forecast

    @staticmethod
    def get_this_forecast_data(of_date):
        forecast_data = ForecastData.query.filter_by(date=of_date).first()
        return forecast_data

    @staticmethod
    def get_all_data():
        data = ForecastData.query.all()
        return data

# ========================== ForecastData Class Ends Here ==================================


# ========================== Top product Class Starts From Here =============================
class TopProducts(db.Model):
    sno = db.Column("sno", db.Integer, primary_key=True, autoincrement=True)
    store = db.Column("store", db.String(5), primary_key=True)
    prod_id = db.Column("prod_id", db.String(5), nullable=False)
    prod_name = db.Column("prod_name", db.String(35), nullable=False)
    total_sold = db.Column("total_sold", db.Integer, nullable=False)
    date = db.Column("date", db.String(16), nullable=False)
    prod_no = db.Column("prod_no", db.Integer, nullable=False)

    @staticmethod
    def save_previous_day_top_prod(n):
        date_now = date.today()
        yesterday_date = date_now - timedelta(n)
        previous_top_prod = TopProducts.query.filter_by(date=yesterday_date).first()
        user_data = Users.get_user_data(session["user"])
        store = Stores.get_store_data(user_data.working_store_id)
        if previous_top_prod:
            return True
        else:
            get_max_sold = ProdSalesByDate.query.filter_by(date=yesterday_date).filter_by(store=store.store_id)\
                .order_by(desc(ProdSalesByDate.total_sold)).first()
            # save top product of day
            if get_max_sold:
                top_prod = Products.get_this_product(get_max_sold.prod_id)

                save_query = TopProducts(store=store.store_id, prod_id=get_max_sold.prod_id,
                                         prod_name=top_prod.prod_name,
                                         total_sold=get_max_sold.total_sold, date=yesterday_date, prod_no=top_prod.sno)
                db.session.add(save_query)
                db.session.commit()
                return True
            else:
                n = n + 1
                TopProducts.save_previous_day_top_prod(n)
                return True

    @staticmethod
    def get_this_store_top_products(store_id):
        store_top_prod = TopProducts.query.filter_by(store=store_id).all()
        return store_top_prod


# ========================== Top product Class Ends Here =============================
