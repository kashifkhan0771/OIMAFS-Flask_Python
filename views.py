"""
This file named views is the most important file of application.
This file contain all views of application mean rendering templates and getting data from models files etc...
This file is joined with all other files.
Basically this file define views of application and dynamically handle them
"""
# ========== Try Block To Import Files ==========
# This try block will check for all files that are being importing.
# If any of file is missing it terminates the app
try:
    from bootstrap import *
    from models import *
    from mailing import *
    from forecasting import generate_forecast_data
    import os  # For Image Uploading
    import pdfkit  # To Generate Pdf Files
except FileExistsError or FileNotFoundError or ImportError:
    print("Please Check For All Of The Files Of Project")
    exit()
# ===============================================

# ========== Some Important Keyword ==========
# page_data = A dictionary that contain dynamic values of some variables for every single web page like page_title etc.
# session = A build in dictionary of flask that contain the information of user who is currently using application.
# flash = This flash is a build in function of flask module that generate a alert type message at front end.
# render_template = A build in function of flask that joins the backend code of route with its front end view.
# <DataType:VariableName> = This is for those routes which are dynamic for everyone to check which user is accessing.
# chart_data = A dictionary that contain data for charts on front end to easily separate it from other data.
# ============================================

# ========== Defining Views Class ==========


# The view class contain all views or you can say routes of application
class Views:
    # =============================== / General Route View ===============================
    @staticmethod
    @app.route("/", methods=["GET", "POST"])
    def login():
        page_data = {"page_title": "LogIn"}  # page data
        if request.method == "POST":
            entered_username = str(request.form.get("entered-username"))
            entered_password = request.form.get("entered-password")
            # Now with divide and conquer method we will divide user into its type and then validate him/her
            # ===== if user is admin =====
            if entered_username.endswith("@admin"):
                entered_username, user_type = entered_username.split("@")  # splitting username and type
                if Admins.validate_admin(entered_username, entered_password):
                    session["user"] = entered_username  # adding user to session
                    session["user_type"] = user_type  # adding user type to session
                    Logs.save_log("Login Detected", session["user_type"], session["user"])
                    return redirect(url_for("admin_dashboard", admin_id=session["user"]))  # get to admin dashboard
                else:
                    make_sound()
                    flash("UserName Or Password Is Incorrect", category="danger")
            # ===== if user is admin =====
            # ===== if user is simple user =====
            elif entered_username.endswith("@user"):
                entered_username, user_type = entered_username.split("@")  # splitting username and type
                if Users.validate_user(entered_username, entered_password):  # validating user from database
                    session["user"] = entered_username  # adding user to session
                    session["user_type"] = user_type  # adding user type to session
                    Logs.save_log("Login Detected", session["user_type"],  session["user"])
                    return redirect(url_for("user_dashboard", user_id=session["user"]))  # get to user dashboard
                else:
                    make_sound()  # a function defined in bootstrap file to create sound
                    flash("UserName Or Password Is Incorrect", category="danger")
                    flash("If You Are Sure About Your User Id And Password Check From Admin If Your Account Is Active",
                          category="info")
            # ===== if user is simple user =====
            else:
                make_sound()
                flash("UserName or Password Is Incorrect", category="danger")

        return render_template("login.html", page_data=page_data)
    # =============================== General Route View Ends Here ===============================

    # =============================== /forget-identity Route View ==============================
    @staticmethod
    @app.route("/forget-identity", methods=["GET", "POST"])
    def forget_identity():
        page_data = {"page_title": "Forget Identity"}
        if request.method == "POST":
            forget_username = request.form.get("forget-username")
            if str(forget_username).endswith("@admin"):
                admin_id, user_type = str(forget_username).split("@")
                admin_data = Admins.get_admin_data(admin_id)
                if admin_data:
                    if admin_data.admin_email:
                        if send_forget_password(params["mail-username"], admin_data.admin_email,
                                                admin_data.admin_password):
                            flash("Your Password Has Been Send To You On " + admin_data.admin_email[0:3] + "****.com",
                                  category="success")
                        else:
                            make_sound()
                            flash("Some Error Occur While Sending Your Password On Mail", category="danger")
                            flash("Please Check Your Internet Connection", category="danger")
                    else:
                        make_sound()
                        flash("No Email Found Related To You On Database", category="warning")
                else:
                    make_sound()
                    flash("The username you have entered is wrong", category="danger")
            else:
                make_sound()
                flash("Forget Password Functionality Is Only For Admins", category="danger")
        return render_template("forget_password.html", page_data=page_data)
    # =============================== /forget-identity Route View Ends Here ==============================

    # =============================== /profile Route View ==============================
    @staticmethod
    @app.route("/profile", methods=["GET", "POST"])
    def profile():
        if "user" in session:
            page_data = {"page_title": "Profile " + str(session["user"]), "page_heading": "Your Profile"}
            if session["user_type"] == "admin":
                admin_data = Admins.get_admin_data(session["user"])
                profile_data = Admins.get_admin_data(session["user"])
                if request.method == "POST":
                    admin_password = request.form.get("user-password")
                    admin_name = request.form.get("user-name")
                    admin_phno = request.form.get("user-phno")
                    admin_gender = request.form.get("user-gender")
                    admin_email = request.form.get("user-email")
                    if Admins.update_admin_data(admin_password, admin_name, admin_phno, admin_gender, admin_email):
                        Logs.save_log("Profile Updated", session["user_type"], session["user"])
                        flash("Profile Updated Successfully", category="success")
                        return redirect(url_for("profile"))
                    else:
                        flash("Some Error Occur while updating your profile, Please login again", category="danger")
                        return redirect(url_for("login"))
                else:
                    return render_template("profile_admin.html", page_data=page_data, admin_data=admin_data,
                                           profile_data=profile_data)
            elif session["user_type"] == "user":
                user_data = Users.get_user_data(session["user"])
                profile_data = Users.get_user_data(session["user"])
                if request.method == "POST":
                    old_id = session["user"]
                    new_id = request.form.get("user-id")
                    user_password = request.form.get("user-password")
                    user_name = request.form.get("user-name")
                    user_phno = request.form.get("user-phno")
                    user_hiredate = request.form.get("user-hiredate")
                    user_gender = request.form.get("user-gender")
                    user_status = request.form.get("user-status")
                    working_store_id = request.form.get("working-store-id")
                    user_email = request.form.get("user-email")
                    user_address = request.form.get("user-address")
                    if Users.update_user(old_id, new_id, user_password, user_name, user_phno, user_hiredate,
                                         user_gender, user_status, working_store_id, user_email, user_address):
                        flash("Profile Updated Successfully", category="success")
                        Logs.save_log("Profile Updated", session["user_type"], session["user"])
                        return redirect(url_for("profile"))
                    else:
                        flash("Some Error Occur While Updating Profile, Please login again", category="danger")
                        return redirect(url_for("login"))
                else:
                    return render_template("profile_user.html", page_data=page_data, user_data=user_data,
                                           profile_data=profile_data)
        else:
            return redirect(url_for("login"))
    # =============================== /profile Route View Ends Here ==============================

    # =============================== /user/<username> Route View ===============================
    @staticmethod
    @app.route("/user/<string:user_id>", methods=["GET", "POST"])
    def user_dashboard(user_id):
        if "user" in session and user_id == session["user"] and session["user_type"] == "user":
            user_data = Users.get_user_data(user_id)  # getting specific user data from database
            page_data = {"page_title": str(user_data.user_name) + " Dashboard", "page_heading": "Dashboard"}
            dashboard_data = Users.generate_user_dashboard_data()
            return render_template("user_dashboard.html", page_data=page_data, user_data=user_data,
                                   dashboard_data=dashboard_data)
        else:
            return redirect(url_for("login"))

    # =============================== /user/<username> View Ends Here ===============================

    # =============================== /admin/<username> Route View ===============================
    @staticmethod
    @app.route("/admin/<string:admin_id>", methods=["GET", "POST"])
    def admin_dashboard(admin_id):
        if "user" in session and admin_id == session["user"] and session["user_type"] == "admin":
            admin_data = Admins.get_admin_data(admin_id)  # getting admin data from database
            page_data = {"page_title": str(admin_data.admin_name) + " Dashboard", "page_heading": "Dashboard"}
            dashboard_data = Admins.generate_admin_dashboard_data()
            return render_template("admin_dashboard.html", page_data=page_data, admin_data=admin_data,
                                   dashboard_data=dashboard_data)

        else:
            return redirect(url_for("login"))

    # =============================== /admin/<username> Route View Ends Here ===============================

    # =============================== /manage-stores Route View ===============================
    @staticmethod
    @app.route("/manage-stores", methods=["GET", "POST"])
    def manage_stores():
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Manage Stores", "page_heading": "Manage Stores"}
            admin_data = Admins.get_admin_data(session["user"])
            stores_data = Stores.get_all_stores_data()
            if request.method == "POST":
                store_id = request.form.get("store-id")
                store_location = request.form.get("store-location")
                store_status = request.form.get("store-status")
                if Stores.save_new_store(store_id, store_location, store_status):
                    flash("New Store Added Successfully", category="success")
                    Logs.save_log("New Store (" + store_id + ") Added", session["user_type"],  session["user"])
                    return redirect(url_for("manage_stores"))
                else:
                    make_sound()
                    flash("Some Error Occur While Adding New Store", category="danger")
                    flash("This Might Occur Due To Same Store Id Please Give New Id To New Store", category="info")
                    Logs.save_log("Error While Adding New Store", session["user_type"], session["user"])
                    return redirect(url_for("manage_stores"))
            else:
                return render_template("manage_stores.html", page_data=page_data, admin_data=admin_data,
                                       stores_data=stores_data)  # sending all required data
        else:
            return redirect(url_for("login"))

    # =============================== /manage-stores Route View ends here ===============================

    # =============================== /delete-store/<store_id> Route ===============================
    @staticmethod
    @app.route("/delete-store/<string:store_id>", methods=["GET", "POST"])
    def delete_store(store_id):
        if "user" in session and session["user_type"] == "admin":
            if Stores.delete_this_store(store_id):
                Logs.save_log("Store (" + store_id + ") Deleted", session["user_type"],  session["user"])
                flash("Store Deleted Successfully", category="success")
                return redirect(url_for("manage_stores"))
        else:
            return redirect(url_for("login"))
    # =============================== /delete-store/<store_id> Route Ends Here ===============================

    # =============================== /details-store/<store_id> Route View ===============================
    @staticmethod
    @app.route("/details-store/<string:store_id>", methods=["GET", "POST"])
    def details_store(store_id):
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Store Details : " + store_id, "page_heading": "Store Details"}
            store_data = Stores.get_store_data(store_id)
            all_store_data_by_date = StoreByDateDetails.get_all_store_data_by_date(store_id)
            total_users = Users.count_users(store_id)
            admin_data = Admins.get_admin_data(session["user"])
            store_top_prod = TopProducts.get_this_store_top_products(store_id)
            if request.method == "POST":
                new_store_id = request.form.get("store-id")
                store_status = request.form.get("store-status")
                store_location = request.form.get("store-location")
                if Stores.update_store_data(store_id, new_store_id, store_status, store_location):
                    Logs.save_log("Store (" + store_id + ") Details Updated", session["user_type"],  session["user"])
                    flash("Store Details Updated Successfully", category="success")
                    return redirect(url_for("details_store", store_id=new_store_id))
                else:
                    make_sound()
                    Logs.save_log("Error During Updating Store (" + store_id + ") Data", session["user_type"],
                                  session["user"])
                    flash("Some Error Occur While Updating Store Data...Please Refresh Application", category="danger")
                    return redirect(url_for("details_store", store_id=store_id))
            # ===== for charts =====
            chart_data = {
                "legend1": "Store Revenue And Profit Chart",
                "labels1": ["Revenue", "Profit"],
                "values1":  [store_data.store_gen_rev, store_data.store_gen_profit],
                "legend2_1": "Store By Date Revenue Last 10 Days",
                "legend2_2": "Store By Date Profit Last 10 Days",
                "labels2": list(),
                "labels2_2": list(),
                "values2_1": list(),
                "values2_2": list(),
                "values2_3": list()
            }
            for d in all_store_data_by_date:
                chart_data["labels2"].append(d.date)
                chart_data["labels2_2"].append(d.date)
                chart_data["values2_1"].append(d.gen_rev)
                chart_data["values2_2"].append(d.gen_profit)
                chart_data["values2_3"].append(d.total_sold)

            # ===== charts data end here =====
            chart_data["labels2"] = chart_data["labels2"][0:6]
            chart_data["labels2_2"] = chart_data["labels2_2"][0:10]
            chart_data["values2_1"] = chart_data["values2_1"][0:10]
            chart_data["values2_2"] = chart_data["values2_2"][0:10]
            chart_data["values2_3"] = chart_data["values2_3"][0:6]
            # Reversing All Values To Show Desc In Graph
            chart_data["labels2"].reverse()
            chart_data["labels2_2"].reverse()
            chart_data["values2_1"].reverse()
            chart_data["values2_2"].reverse()
            chart_data["values2_3"].reverse()
            # Reversing All Values To Show Desc In Graph
            return render_template("details_store.html", admin_data=admin_data, store_data=store_data,
                                   page_data=page_data, chart_data=chart_data,
                                   all_store_data_by_date=all_store_data_by_date, total_users=total_users,
                                   top_prod=store_top_prod)
        else:
            return redirect(url_for("login"))

    # =============================== /details-store/<store_id> Route View Ends Here ===============================

    # =============================== /manage-brands Route View ===============================
    @staticmethod
    @app.route("/manage-brands", methods=["GET", "POST"])
    def manage_brands():
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Manage Brands", "page_heading": "Manage Brands"}
            admin_data = Admins.get_admin_data(session["user"])
            all_brands = Brands.get_all_brands()
            if request.method == "POST":
                brand_id = request.form.get("brand-id")
                brand_status = request.form.get("brand-status")
                brand_name = request.form.get("brand-name")
                brand_img = request.files["brand_img"]
                # ===== Checking Image Format =====
                if brand_img:
                    if str(brand_img.filename).endswith(".jpg") or str(brand_img.filename).endswith(".png"):
                        brand_img.save(os.path.join(app.config['IMG_UPLOAD_FOLDER'], brand_img.filename))
                    else:
                        flash("File Format Not Supported", category="danger")
                        return redirect(url_for("manage_brands"))
                # ===== Checking Image Format =====
                brand_img_url = brand_img.filename
                if Brands.save_new_brand(brand_id, brand_status, brand_name, brand_img_url):
                    Logs.save_log("New Brand (" + brand_name + ") Added", session["user_type"],  session["user"])
                    flash("New Brand Added Successfully", category="success")
                    return redirect(url_for("manage_brands"))
                else:
                    make_sound()
                    Logs.save_log("Some Error Occur While Adding New Brand", session["user_type"],  session["user"])
                    flash("Some Error Occur While Adding New Brand", category="danger")
                    flash("This Might Occur Due To Brand Id Redundancy", category="info")
                    return redirect(url_for("manage_brands"))
            else:
                return render_template("manage_brands.html", all_brands=all_brands, page_data=page_data,
                                       admin_data=admin_data)
        else:
            return redirect(url_for("login"))
    # =============================== /manage-brands Route View Ends Here ===============================

    # =============================== /details-brand/<string:brand_id> Route View ===============================
    @staticmethod
    @app.route("/details-brand/<string:brand_id>", methods=["GET", "POST"])
    def details_brand(brand_id):
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Details Brand : " + brand_id, "page_heading": "Brand Details"}
            admin_data = Admins.get_admin_data(session["user"])
            brand_data = Brands.get_this_brand(brand_id)
            total_products = Products.count_brand_products(brand_data.brand_name)
            brand_prods = Brands.get_brand_prod_details(brand_id)
            if request.method == "POST":
                new_brand_id = request.form.get("brand-id")
                brand_status = request.form.get("brand-status")
                brand_name = request.form.get("brand-name")
                brand_img = request.files["updated_brand_img"]
                # ===== Checking Image Format Starts =====
                if brand_img:
                    if str(brand_img.filename).endswith(".jpg") or str(brand_img.filename).endswith(".png"):
                        brand_img.save(os.path.join(app.config['IMG_UPLOAD_FOLDER'], brand_img.filename))
                    else:
                        make_sound()
                        flash("File Format Not Supported", category="danger")
                        return redirect(url_for("details_brand", brand_id=brand_id))
                # ===== Checking Image Format Ends =====
                brand_img_url = brand_img.filename
                if Brands.update_brand_data(brand_id, new_brand_id, brand_status, brand_name, brand_img_url):
                    Logs.save_log("Brand (" + brand_name + ") Details Updated", session["user_type"],  session["user"])
                    flash("Brand Details Updated Successfully", category="success")
                    return redirect(url_for("details_brand", brand_id=new_brand_id))
                else:
                    make_sound()
                    Logs.save_log("Some Error Occur While Updating Store Data", session["user_type"],  session["user"])
                    flash("Some Error Occur While Updating Brand Data...Refresh Application", category="danger")
                    return redirect(url_for("details_brand", brand_id=brand_id))

            return render_template("details_brand.html", admin_data=admin_data, page_data=page_data,
                                   brand_data=brand_data, total_products=total_products, brand_prods=brand_prods)
        else:
            return redirect(url_for("login"))
    # =============================== /details-brand/<string:brand_id> Route View ===============================

    # =============================== /delete-brand/<string:brand_id> Route ===============================
    @staticmethod
    @app.route("/delete-brand/<string:brand_id>")
    def delete_brand(brand_id):
        if "user" in session and session["user_type"] == "admin":
            if Brands.delete_this_brand(brand_id):
                Logs.save_log("Brand (" + brand_id + ") Deleted Successfully", session["user_type"],  session["user"])
                flash("Brand Deleted Successfully", category="info")
                return redirect(url_for("manage_brands"))
        else:
            return redirect(url_for("login"))
    # =============================== /delete-brand/<string:brand_id> Route ===============================

    # =============================== /manage-products Route View ===============================
    @staticmethod
    @app.route("/manage-products", methods=["GET", "POST"])
    def manage_products():
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Manage Products", "page_heading": "Manage Products"}
            admin_data = Admins.get_admin_data(session["user"])
            all_products = Products.get_all_products()
            all_brands = Brands.get_active_brands()
            if request.method == "POST":
                prod_id = request.form.get("product-id")
                prod_loc = request.form.get("product-loc")
                prod_name = request.form.get("product-name")
                prod_brand = request.form.get("product-brand")
                buy_price = request.form.get("buy-price")
                sell_price = request.form.get("sell-price")
                qty_total = request.form.get("product-in-hand")
                discount_price = request.form.get("product-discount")
                color = request.form.get("product-color")
                description = request.form.get("product-description")
                prod_img = request.files["product_img"]
                if int(buy_price) > int(sell_price):
                    make_sound()
                    flash("Selling price Can Not Be Less Than Buying Price", category="warning")
                    return redirect(url_for("manage_products"))
                # ===== Checking Image Format =====
                if prod_img:
                    if str(prod_img.filename).endswith(".jpg") or str(prod_img.filename).endswith(".png"):
                        prod_img.save(os.path.join(app.config['IMG_UPLOAD_FOLDER'], prod_img.filename))
                    else:
                        make_sound()
                        flash("File Format Not Supported", category="danger")
                        return redirect(url_for("manage_products"))
                # ===== Checking Image Format =====
                prod_img_url = prod_img.filename
                if Products.save_new_product(prod_id, prod_loc, prod_name, prod_brand, buy_price, sell_price,
                                             qty_total, discount_price, color, description, prod_img_url):
                    Logs.save_log("New Product (" + prod_name + ") Added Successfully", session["user_type"],
                                  session["user"])
                    flash("New Product Added Successfully", category="success")
                    return redirect(url_for("manage_products"))
                else:
                    make_sound()
                    Logs.save_log("Some Error Occur While Adding New Product", session["user_type"],  session["user"])
                    flash("Some Error Occur While Adding New Product ", category="danger")
                    flash("This May Be Due To Product Id Redundancy", category="info")
                    return redirect(url_for("manage_products"))

            else:
                return render_template("manage_products.html", page_data=page_data, admin_data=admin_data,
                                       all_products=all_products, all_brands=all_brands)
        else:
            return redirect(url_for("login"))
    # =============================== /manage-products Route View Ends Here ===============================

    # =============================== /details-product/<prod_id> Route View ===============================
    @staticmethod
    @app.route("/details-product/<string:prod_id>", methods=["GET", "POST"])
    def details_product(prod_id):
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Details Product : " + prod_id, "page_heading": "Product Details"}
            admin_data = Admins.get_admin_data(session["user"])
            prod_data = Products.get_this_product(prod_id)
            all_brands = Brands.get_active_brands()
            prod_details = ProductsDetails.get_prod_details(prod_id)
            prod_by_date_details = ProdSalesByDate.get_prod_by_date_sales(prod_id)
            chart_data = {
                "labels": [],
                "legend1_1": "Profit By Date",
                "legend1_2": "Revenue By Date",
                "legend1_3": "Total Sold",
                "values1": [],
                "values1_2": [],
                "values1_3": []
            }
            for data in prod_by_date_details:
                chart_data["labels"].append(data.date)
                chart_data["values1"].append(data.gen_profit)
                chart_data["values1_2"].append(data.gen_rev)
                chart_data["values1_3"].append(data.total_sold)
            chart_data["values1"] = chart_data["values1"][0:10]
            chart_data["labels"] = chart_data["labels"][0:10]
            chart_data["values1_2"] = chart_data["values1_2"][0:10]
            chart_data["values1_3"] = chart_data["values1_3"][0:10]
            # Reversing All Values To Show Desc In Graph
            chart_data["values1"].reverse()
            chart_data["labels"].reverse()
            chart_data["values1_2"].reverse()
            chart_data["values1_3"].reverse()
            # Reversing All Values To Show Desc In Graph
            if request.method == "POST":
                new_prod_id = request.form.get("product-id")
                prod_loc = request.form.get("product-loc")
                prod_name = request.form.get("product-name")
                prod_brand = request.form.get("product-brand")
                buy_price = request.form.get("buy-price")
                sell_price = request.form.get("sell-price")
                qty_total = request.form.get("total-qty")
                discount_price = request.form.get("dis-price")
                color = request.form.get("color")
                prod_img = request.files["product_img"]
                if int(buy_price) > int(sell_price):
                    make_sound()
                    flash("Selling price Can Not Be Less Than Buying Price", category="warning")
                    return redirect(url_for("manage_products"))
                # ===== Checking Image Format =====
                if prod_img:
                    if str(prod_img.filename).endswith(".jpg") or str(prod_img.filename).endswith(".png"):
                        prod_img.save(os.path.join(app.config['IMG_UPLOAD_FOLDER'], prod_img.filename))
                    else:
                        make_sound()
                        flash("File Format Not Supported", category="danger")
                        return redirect(url_for("manage_products"))
                # ===== Checking Image Format =====
                prod_img_url = prod_img.filename
                if Products.update_product(prod_id, new_prod_id, prod_loc, prod_name, prod_brand, buy_price,
                                           sell_price, qty_total, discount_price, color, prod_img_url):
                    Logs.save_log("Product (" + prod_name + ") Updated Successfully", session["user_type"],
                                  session["user"])
                    flash("Product Updated Successfully", category="success")
                    return redirect(url_for("details_product", prod_id=new_prod_id))
                else:
                    make_sound()
                    Logs.save_log("Product (" + prod_name + ") Details Updating Failed", session["user_type"],
                                  session["user"])
                    flash("Some Error Occur While Updating Product, Fill Carefully", category="danger")
                    return redirect(url_for("details_product", prod_id=prod_id))
            else:
                return render_template("details_product.html", admin_data=admin_data, page_data=page_data,
                                       prod_data=prod_data, all_brands=all_brands, chart_data=chart_data,
                                       prod_details=prod_details, prod_by_date_details=prod_by_date_details)
        else:
            return redirect(url_for("login"))
    # =============================== /details-product/<prod_id> Route View Ends Here ===============================

    # =============================== /delete-product/<prod-id> Route ===============================
    @staticmethod
    @app.route("/delete-product/<string:prod_id>", methods=["GET", "POST"])
    def delete_product(prod_id):
        if "user" in session and session["user_type"] == "admin":
            if Products.delete_this_product(prod_id):
                Logs.save_log("Product (" + prod_id + ") Deleted Successfully", session["user_type"], session["user"])
                flash("Product Deleted Successfully", category="info")
                return redirect(url_for("manage_products"))
        else:
            return redirect(url_for("login"))
    # =============================== /delete-product/<prod-id> Route ===============================

    # =============================== /manage-member Route View =========================================
    @staticmethod
    @app.route("/manage-members", methods=["GET", "POST"])
    def manage_members():
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Manage Members", "page_heading": "Manage Members"}
            admin_data = Admins.get_admin_data(session["user"])
            members_data = Members.get_all_members_data()
            if request.method == "POST":
                member_id = request.form.get("member-id")
                member_phno = request.form.get("member-phno")
                member_name = request.form.get("member-name")
                member_email = request.form.get("member-email")
                member_address = request.form.get("member-address")
                print(member_address)
                if Members.save_new_member(member_id, member_name, member_phno, member_email,
                                           member_address):
                    Logs.save_log("New Member (" + member_name + ") Added Successfully", session["user_type"],
                                  session["user"])
                    flash("New Member Added Successfully", category="success")
                    return redirect(url_for("manage_members"))
                else:
                    make_sound()
                    flash("Some Error Occur While Adding New Member", category="danger")
                    flash("This May Be Due To Member Id Redundancy", category="info")
                    return redirect(url_for("manage_members"))
            else:
                return render_template("manage_members.html", page_data=page_data, admin_data=admin_data,
                                       members_data=members_data)
        else:
            return redirect(url_for("login"))

    # =============================== /manage-member Route View Ends Here =========================================

    # =============================== /delete-member/<string:member_id> Route ============================
    @staticmethod
    @app.route("/delete-member/<string:member_id>", methods=["GET", "POST"])
    def delete_member(member_id):
        if "user" in session and session["user_type"] == "admin":
            if Members.delete_this_member(member_id):
                Logs.save_log("Member (" + member_id + ") Deleted Successfully", session["user_type"], session["user"])
                flash("Member Deleted Successfully", category="success")
                return redirect(url_for("manage_members"))
            else:
                make_sound()
                Logs.save_log("Some Error Occur While Deleting Member", session["user_type"], session["user"])
                flash("Some Error Occur While Deleting", category="danger")
                return redirect(url_for("manage_member"))

    # =============================== /delete-member/<string:member_id> Route Ends Here ======================

    # =============================== /detail-member<string:member_id> Route View ============================
    @staticmethod
    @app.route("/details-member/<string:member_id>", methods=["GET", "POST"])
    def details_member(member_id):
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Details Member : " + str(member_id), "page_heading": "Member Details"}
            admin_data = Admins.get_admin_data(session["user"])
            member_data = Members.get_this_members_data(member_id)
            member_sales_data = MembersSalesDetail.get_member_sales_data(member_id)
            if request.method == "POST":
                new_member_id = request.form.get("member-id")
                member_phno = request.form.get("member-phno")
                member_name = request.form.get("member-name")
                member_email = request.form.get("member-email")
                member_address = request.form.get("member-address")
                if Members.update_member(member_id, new_member_id, member_name, member_email, member_phno,
                                         member_address):
                    Logs.save_log("Member (" + member_name + ") Details Updated Successfully", session["user_type"],
                                  session["user"])
                    flash("Member Data Updated Successfully", category="success")
                    return redirect(url_for("details_member", member_id=new_member_id))
                else:
                    Logs.save_log("Some Error Occur While Updating Member Details", session["user_type"],
                                  session["user"])
                    flash("Sorry Member Data Did't Get Updated", category="danger")
            else:
                return render_template("details_member.html", page_data=page_data, admin_data=admin_data,
                                       member_data=member_data, member_sales_data=member_sales_data)
        else:
            return redirect(url_for("login"))
    # =============================== /detail-member<string:member_id> Route View Ends Here ======================

    # =============================== /manage-users Route View ================================
    @staticmethod
    @app.route("/manage-users", methods=["GET", "POST"])
    def manage_users():
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Manage Users", "page_heading": "Manage Users"}
            admin_data = Admins.get_admin_data(session["user"])
            all_users = Users.get_all_user_data()
            all_stores = Stores.get_all_stores_data()
            if request.method == "POST":
                user_id = request.form.get("user-id")
                user_password = request.form.get("user-password")
                user_name = request.form.get("user-name")
                user_phno = request.form.get("user-phno")
                user_hiredate = request.form.get("user-hiredate")
                user_gender = request.form.get("user-gender")
                user_status = request.form.get("user-status")
                working_store_id = request.form.get("working-store-id")
                user_email = request.form.get("user-email")
                user_address = request.form.get("user-address")
                if Users.save_new_user(user_id, user_password, user_name, user_phno, user_hiredate, user_gender,
                                       user_status, working_store_id, user_email, user_address):
                    flash("New User Added Successfully", category="info")
                    Logs.save_log("New User (" + user_name + ") Added Successfully", session["user_type"],
                                  session["user"])
                else:
                    flash("Some Error Occur While Adding New User", category="danger")
                    flash("This Might Occur Due To Duplicate Id, Please Fill Form Carefully", category="info")
                    Logs.save_log("Try To Add New User, But Failed", session["user_type"], session["user"])

                return redirect(url_for("manage_users"))
            else:
                return render_template("manage_users.html", page_data=page_data, admin_data=admin_data,
                                       all_users=all_users, all_stores=all_stores)
        else:
            return redirect(url_for("login"))
    # =============================== /manage-users Route View Ends Here ================================

    # =============================== /details-user/<string:user_id> Route View ================================
    @staticmethod
    @app.route("/details-user/<string:user_id>", methods=["GET", "POST"])
    def details_user(user_id):
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Details User : " + user_id, "page_heading": "User Details"}
            admin_data = Admins.get_admin_data(session["user"])
            user_data = Users.get_user_data(user_id)
            all_stores = Stores.get_all_stores_data()
            user_invoices = Invoices.get_this_user_invoices(user_id)
            if request.method == "POST":
                new_id = request.form.get("user-id")
                user_password = request.form.get("user-password")
                user_name = request.form.get("user-name")
                user_phno = request.form.get("user-phno")
                user_hiredate = request.form.get("user-hiredate")
                user_gender = request.form.get("user-gender")
                user_status = request.form.get("user-status")
                working_store_id = request.form.get("working-store-id")
                user_email = request.form.get("user-email")
                user_address = request.form.get("user-address")
                if Users.update_user(user_id, new_id, user_password, user_name, user_phno, user_hiredate,
                                     user_gender, user_status, working_store_id, user_email, user_address):
                    flash("User Updated Successfully", category="success")
                    Logs.save_log("User (" + user_name + ") Details Updated", session["user_type"], session["user"])
                    return redirect(url_for("details_user", user_id=new_id))
                else:
                    flash("Some Error Occur While Updating", category="danger")
                    flash("This Might Happen Due To Duplicate Id", category="info")
                    Logs.save_log("User (" + user_name + ") Details Update Failed", session["user_type"],
                                  session["user"])
                    return redirect(url_for("details_user", user_id=user_id))
            else:
                return render_template("detail_user.html", page_data=page_data, admin_data=admin_data,
                                       user_data=user_data, user_invoices=user_invoices, all_stores=all_stores)
        else:
            return redirect(url_for("login"))
    # ============================ /details-user/<string:user_id> Route View Ends Here ================================

    # =============================== /delete-users<string:user-id> Route ================================
    @staticmethod
    @app.route("/delete-user/<string:user_id>")
    def delete_user(user_id):
        if "user" in session and session["user_type"] == "admin":
            if Users.delete_this_user(user_id):
                Logs.save_log("User (" + user_id + ") Deleted Successfully", session["user_type"], session["user"])
                flash("User Deleted Successfully", category="success")
                return redirect(url_for("manage_users"))
            else:
                flash("User Deletion Failed, The User Might Not Exist, Refresh Application", category="info")
                return redirect(url_for("manage_users"))
        else:
            return redirect(url_for("login"))
    # =============================== /delete-users<string:user-id> Route Ends Here ================================

    # =============================== /reports-draft Route View ================================
    @staticmethod
    @app.route("/reports-draft/<string:gen_by>", methods=["GET", "POST"])
    def reports_draft(gen_by):
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Reports Draft", "page_heading": "Your Previously Generated Reports Draft"}
            admin_data = Admins.get_admin_data(session["user"])
            all_reports = ReportsDraft.get_reports_by(gen_by)

            return render_template("reports_draft.html", page_data=page_data, admin_data=admin_data,
                                   all_reports=all_reports)
        else:
            return redirect(url_for("login"))
    # =============================== /reports-draft Route View Ends Here ================================

    # =============================== /delete-report Route ================================
    @staticmethod
    @app.route("/delete-report/<string:sno>")
    def delete_report(sno):
        if "user" in session and session["user_type"] == "admin":
            if ReportsDraft.delete_this_report(sno):
                flash("Report Deleted Successfully", category="success")
                Logs.save_log("Report Deleted Successfully", session["user_type"], session["user"])
                return redirect(url_for("reports_draft", gen_by=session["user"]))
            else:
                flash("Sorry Report Cannot Be Deleted", category="danger")
                return redirect(url_for("reports_draft", gen_by=session["user"]))

    # =============================== /delete-report Route Ends Here ================================

    # =============================== /store-report Route View ================================
    @staticmethod
    @app.route("/store-report", methods=["GET", "POST"])
    def store_report():
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Store Report", "page_heading": "Generate Store Report"}
            admin_data = Admins.get_admin_data(session["user"])
            all_stores = Stores.get_all_stores_data()
            if request.method == "POST":
                from_date = request.form.get("from-date")
                to_date = request.form.get("to-date")
                store = request.form.get("store")
                if ReportsDraft.check_dates_for_reports(from_date, to_date):
                    ReportsDraft.save_report_to_draft(from_date, to_date, session["user"], store, "Store")
                    Logs.save_log("New Store Report Generated", session["user_type"], session["user"])
                else:
                    flash("Please Enter Dates Correctly", category="warning")
                    return redirect(url_for("reports_draft", gen_by=session["user"]))
                report_sno = ReportsDraft.get_last_report_sno()
                return redirect(url_for("download_report", sno=report_sno))
            else:
                return render_template("store_report.html", page_data=page_data, admin_data=admin_data,
                                       all_stores=all_stores)
        else:
            return redirect(url_for("login"))

    # =============================== /store-report Route View Ends Here ================================

    # =============================== /product-report Route View ================================
    @staticmethod
    @app.route("/product-report", methods=["GET", "POST"])
    def product_report():
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Product Report", "page_heading": "Generate Product Report"}
            admin_data = Admins.get_admin_data(session["user"])
            all_products = Products.get_all_products()
            if request.method == "POST":
                from_date = request.form.get("from-date")
                to_date = request.form.get("to-date")
                product = request.form.get("product")
                if ReportsDraft.check_dates_for_reports(from_date, to_date):
                    ReportsDraft.save_report_to_draft(from_date, to_date, session["user"], product, "Product")
                    Logs.save_log("New Product Report Generated", session["user_type"], session["user"])
                else:
                    flash("Please Enter Dates Correctly", category="warning")
                    return redirect(url_for("reports_draft", gen_by=session["user"]))
                report_sno = ReportsDraft.get_last_report_sno()
                return redirect(url_for("download_report", sno=report_sno))
            else:
                return render_template("product_report.html", page_data=page_data, admin_data=admin_data,
                                       all_products=all_products)
        else:
            return redirect(url_for("login"))
    # =============================== /product-report Route View Ends Here ================================

    # =============================== /download-report Route ================================
    @staticmethod
    @app.route("/download-report/<string:sno>")
    def download_report(sno):
        if "user" in session and session["user_type"] == "admin":
            data = ReportsDraft.generate_this_report(sno)
            if data is False:
                flash("Please Enter Information Correctly To Generate Report", category="danger")
                return redirect(url_for("reports_draft", gen_by=session["user"]))
            report_data = ReportsDraft.get_report_data_from_draft(sno)
            template = ''  # just to handle warning below on line where template is been converted to pdf
            if report_data.type_of == "Store":
                template = render_template("download_store_report.html", report_data=report_data, data=data)
            elif report_data.type_of == "Product":
                print(data)
                template = render_template("download_prod_report.html", report_data=report_data, data=data)
            elif report_data.type_of == "Member":
                template = render_template("download_member_report.html", report_data=report_data, data=data)
            path_wkhtmltopdf = params["path_to_wkhtmltopdf"]
            config_path = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
            report_pdf = pdfkit.from_string(template, False, configuration=config_path)

            response = make_response(report_pdf)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % "StoreReport"
            return response
        else:
            return redirect(url_for("login"))
        # =============================== /download-report Route Ends Here ================================

    # =============================== /messages-inbox/<string:message_to> Route View ================================
    @staticmethod
    @app.route("/messages-inbox/<string:message_to>", methods=["GET", "POST"])
    def messages_inbox(message_to):
        if "user" in session and message_to == session["user"]:
            if session["user_type"] == "admin":
                page_data = {"page_title": "Messages Inbox", "page_heading": "Messages For You"}
                admin_data = Admins.get_admin_data(session["user"])
                send_to_list = Users.get_all_user_data()
                messages = Messages.get_messages_for(message_to)
                if request.method == "POST":
                    msg_from = request.form.get("msg-from")
                    msg_to = request.form.get("msg-to")
                    msg_subject = request.form.get("msg-subject")
                    msg_body = request.form.get("msg-body")
                    if Messages.send_new_message(msg_from, msg_to, msg_subject, msg_body):
                        flash("Message Sent Successfully", category="success")
                        Logs.save_log("Message Sent To " + msg_to + " Successfully", session["user_type"],
                                      session["user"])
                        make_sound()
                    else:
                        Logs.save_log("Message Sending Failed", session["user_type"], session["user"])
                        flash("Message Cannot Be Sent, Sorry", category="danger")
                    return redirect(url_for("messages_inbox", message_to=session["user"]))
                else:
                    return render_template("messages_inbox_admin.html", page_data=page_data, admin_data=admin_data,
                                           send_to_list=send_to_list, messages=messages)
            elif session["user_type"] == "user":
                page_data = {"page_title": "Messages", "page_heading": "Messages For You"}
                user_data = Users.get_user_data(session["user"])
                send_to_list = Admins.get_all_admins_data()
                messages = Messages.get_messages_for(message_to)
                if request.method == "POST":
                    msg_from = request.form.get("msg-from")
                    msg_to = request.form.get("msg-to")
                    msg_subject = request.form.get("msg-subject")
                    msg_body = request.form.get("msg-body")
                    if Messages.send_new_message(msg_from, msg_to, msg_subject, msg_body):
                        flash("Message Sent Successfully", category="success")
                        Logs.save_log("Message Sent To " + msg_to + " Successfully", session["user_type"],
                                      session["user"])
                        make_sound()
                    else:
                        Logs.save_log("Message Sending Failed", session["user_type"], session["user"])
                        flash("Message Cannot Be Sent, Sorry", category="danger")
                    return redirect(url_for("messages_inbox", message_to=session["user"]))
                else:
                    return render_template("messages_inbox_user.html", page_data=page_data, user_data=user_data,
                                           send_to_list=send_to_list, messages=messages)
        else:
            return redirect(url_for("login"))

    # =============================== /messages-inbox/<string:message_to> Route View Ends Here  =======================

    # =============================== /messages-sent/<string:message_from> Route View ================================
    @staticmethod
    @app.route("/messages-sent/<string:message_from>", methods=["GET", "POST"])
    def messages_sent(message_from):
        if "user" in session and message_from == session["user"]:
            if session["user_type"] == "admin":
                page_data = {"page_title": "Messages Sent", "page_heading": "Your Sent Messages"}
                admin_data = Admins.get_admin_data(session["user"])
                send_to_list = Users.get_all_user_data()
                messages = Messages.get_send_messages(message_from)
                if request.method == "POST":
                    msg_from = request.form.get("msg-from")
                    msg_to = request.form.get("msg-to")
                    msg_subject = request.form.get("msg-subject")
                    msg_body = request.form.get("msg-body")
                    if Messages.send_new_message(msg_from, msg_to, msg_subject, msg_body):
                        Logs.save_log("Message Sent To " + msg_to + " Successfully", session["user_type"],
                                      session["user"])
                        flash("Message Sent Successfully", category="success")
                        make_sound()
                    else:
                        Logs.save_log("Message Sending Failed", session["user_type"], session["user"])
                        flash("Message Cannot Be Sent, Sorry", category="danger")
                    return redirect(url_for("messages_sent", message_from=session["user"]))
                else:
                    return render_template("messages_sent_admin.html", page_data=page_data, admin_data=admin_data,
                                           send_to_list=send_to_list, messages=messages)
            elif session["user_type"] == "user":
                page_data = {"page_title": "Messages Sent", "page_heading": "Your Sent Messages"}
                user_data = Users.get_user_data(session["user"])
                send_to_list = Admins.get_all_admins_data()
                messages = Messages.get_send_messages(message_from)
                if request.method == "POST":
                    msg_from = request.form.get("msg-from")
                    msg_to = request.form.get("msg-to")
                    msg_subject = request.form.get("msg-subject")
                    msg_body = request.form.get("msg-body")
                    if Messages.send_new_message(msg_from, msg_to, msg_subject, msg_body):
                        Logs.save_log("Message Sent To " + msg_to + " Successfully", session["user_type"],
                                      session["user"])
                        flash("Message Sent Successfully", category="success")
                        make_sound()
                    else:
                        Logs.save_log("Message Sending Failed", session["user_type"], session["user"])
                        flash("Message Cannot Be Sent, Sorry", category="danger")
                    return redirect(url_for("messages_sent", message_from=session["user"]))
                else:
                    return render_template("messages_sent_user.html", page_data=page_data, user_data=user_data,
                                           send_to_list=send_to_list, messages=messages)
        else:
            return redirect(url_for("login"))

    # ============================= /messages-sent/<string:message_from> Route View Ends Here  ========================

    # =============================== /delete-message/<string:message_id> Route ===========================
    @staticmethod
    @app.route("/delete-message/<string:message_id>")
    def delete_message(message_id):
        if "user" in session and session["user_type"] == "admin":
            if Messages.delete_message(message_id):
                Logs.save_log("Message Deleted Successfully", session["user_type"], session["user"])
                flash("Message Deleted Successfully", category="success")
                return redirect(url_for("messages_inbox", message_to=session["user"]))
            else:
                flash("Message Cannot Be Deleted, Please Refresh The Page", category="danger")
                return redirect(url_for("messages_inbox", message_to=session["user"]))
        else:
            return redirect(url_for("login"))

    # =============================== /delete-message/<string:message_id> Route Ends Here ===========================

    # =============================== /read-message/<string:message_id> Route View ===========================
    @staticmethod
    @app.route("/read-message/<string:message_id>")
    def read_message(message_id):
        if "user" in session:
            if session["user_type"] == "admin":
                page_data = {"page_title": "Read Message", "page_heading": "Message View"}
                admin_data = Admins.get_admin_data(session["user"])
                Messages.update_message_status(message_id)
                message = Messages.get_message(message_id)
                sender = Users.get_user_data(message.message_from)
                return render_template("read_message_admin.html", page_data=page_data, admin_data=admin_data,
                                       message=message, sender=sender)
            elif session["user_type"] == "user":
                page_data = {"page_title": "Read Message", "page_heading": "Message View"}
                user_data = Users.get_user_data(session["user"])
                Messages.update_message_status(message_id)
                message = Messages.get_message(message_id)
                sender = Admins.get_admin_data(message.message_from)
                return render_template("read_message_user.html", page_data=page_data, user_data=user_data,
                                       message=message, sender=sender)
            else:
                flash("Please Login Properly", category="warning")
                return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))
    # ============================== /read-message/<string:message_id> Route View Ends Here ===========================

    # =============================== /invoices Route View  ===================================
    @staticmethod
    @app.route("/invoices", methods=["GET", "POST"])
    def invoices():
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Invoices", "page_heading": "Recent Invoices"}
            admin_data = Admins.get_admin_data(session["user"])
            all_invoices = Invoices.get_all_invoices()
            return render_template("invoices.html", page_data=page_data, admin_data=admin_data,
                                   all_invoices=all_invoices)
        else:
            return redirect(url_for("login"))
    # =============================== /invoices Route View Ends Here  ===================================

    # =============================== Logout Route ===============================
    @staticmethod
    @app.route("/logout")
    def logout_from_application():
        Logs.save_log("Logout Detected", session["user_type"],  session["user"])
        session.pop("user", None)
        session.pop("user_type", None)
        return redirect(url_for("login"))

    # =============================== Logout Route Ends Here ===============================

    # =============================== /logs Route View  ===============================
    @staticmethod
    @app.route("/logs", methods=["GET", "POST"])
    def logs():
        if "user" in session and session["user_type"] == "admin":
            all_logs = Logs.get_logs()
            page_data = {"page_title": "Logs", "page_heading": "Logs"}
            admin_data = Admins.get_admin_data(session["user"])
            if request.method == "POST":
                clear_what = request.form.get("clear-log-from")
                if str(clear_what) == "one-date":
                    of_date = request.form.get("one-date")
                    if of_date == "":
                        flash("Please Enter Date", category="warning")
                        return redirect(url_for("logs"))
                    if Logs.clear_one_date_logs(of_date):
                        flash("All Logs Get Clear of Date : " + str(of_date), category="info")
                    else:
                        flash("No Logs Found Of This Specific Date", category="info")
                elif str(clear_what) == "range-date":
                    from_date = request.form.get("from")
                    to_date = request.form.get("to")
                    if from_date == "" or to_date == "":
                        flash("Please Enter Date", category="warning")
                        return redirect(url_for("logs"))
                    if Logs.clear_range_date_logs(from_date, to_date):
                        flash("All Logs Are Deleted From : " + str(from_date) + " To " + str(to_date), category="info")
                    else:
                        flash("Cannot Delete Logs, This Might Happen When You Choose First Date Greater Than Second",
                              category="danger")
                        flash("If Date Are Entered Correctly Then There Is No Log On These Dates", category="info")
                return redirect(url_for("logs"))
            else:
                return render_template("logs.html", page_data=page_data, all_logs=all_logs, admin_data=admin_data)
        else:
            return redirect(url_for("login"))

    # =============================== /logs Route View Ends Here  ===============================

    # =============================== /sell-to-non-members Route View ===============================
    @staticmethod
    @app.route("/sell-to-non-members", methods=["GET", "POST"])
    def sell_to_non_members():
        if "user" in session and session["user_type"] == "user":
            user_data = Users.get_user_data(session["user"])
            page_data = {"page_title": "Sell To Non Members", "page_heading": "Sell Products To Non Members"}
            products = Products.get_prod_for_sale()
            if request.method == "POST":
                buyer_name = request.form.get("buyer-name")
                buyer_phno = request.form.get("buyer-phno")
                buyer_loc = request.form.get("buyer-loc")
                prod_name = request.form.get("prod-name")
                prod_qty = request.form.get("prod-qty")
                if NonMembersData.prod_selling_process(buyer_name, buyer_loc, buyer_phno, prod_name,
                                                       prod_qty):
                    flash("Product Sold Successfully", category="success")
                    Logs.save_log("Product Sold Successfully To Non Member (" + buyer_name + ")",
                                  session["user_type"], session["user"])
                    return redirect(url_for("sell_to_non_members"))
                else:
                    Logs.save_log("Product Selling Failed", session["user_type"],  session["user"])
                    make_sound()
                    flash("Some Error Occur Please Fill Form Carefully", category="danger")
                return redirect(url_for("sell_to_non_members"))
            else:
                return render_template("sell_to_non_members.html", user_data=user_data, page_data=page_data,
                                       products=products)
        else:
            return redirect(url_for("login"))

    # =============================== /sell-to-non-members Route View ===============================

    # =============================== /sell-to-members Route View ===============================
    @staticmethod
    @app.route("/sell-to-members", methods=["GET", "POST"])
    def sell_to_members():
        if "user" in session and session["user_type"] == "user":
            user_data = Users.get_user_data(session["user"])
            page_data = {"page_title": "Sell To Non Members", "page_heading": "Sell Products To Members"}
            members = Members.get_all_members_data()
            products = Products.get_prod_for_sale()
            if request.method == "POST":
                member_name = request.form.get("member-name")
                prod_name = request.form.get("prod-name")
                prod_qty = request.form.get("prod-qty")
                if MembersSalesDetail.prod_selling_process(member_name, prod_name, prod_qty):
                    flash("Product Sold Successfully To Member", category="success")
                    Logs.save_log("Product Sold Successfully To Member (" + member_name + ")",
                                  session["user_type"], session["user"])
                    return redirect(url_for("sell_to_members"))
                else:
                    Logs.save_log("Product Selling Failed", session["user_type"], session["user"])
                    make_sound()
                    flash("Some Error Occur Please Fill Form Carefully", category="danger")
                return redirect(url_for("sell_to_members"))
            else:
                return render_template("sell_to_members.html", user_data=user_data, page_data=page_data,
                                       products=products, members=members)
        else:
            return redirect(url_for("login"))
    # =============================== /sell-to-members Route View Ends Here ===============================

    # =============================== /download-invoice Route ===============================
    @staticmethod
    @app.route("/download-invoice/<string:sno>", methods=["GET", "POST"])
    def download_invoice(sno):
        if "user" in session:
            data = dict()
            if session["user_type"] == "user":
                if sno == "recent":
                    data = Invoices.get_recent_invoice_after_check()
                else:
                    data = Invoices.get_invoice_for_user_after_check(sno)
                    if data is False:
                        flash("Sorry This Invoice Is Not For You", category="info")
                        return redirect(url_for("view_invoices"))
            elif session["user_type"] == "admin":
                if sno == "recent":
                    data = Invoices.get_recent_invoice()
                else:
                    data = Invoices.get_this_invoice(sno)
            template = render_template("download_recent_invoice.html", data=data)
            path_wkhtmltopdf = params["path_to_wkhtmltopdf"]
            config_path = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
            invoice_pdf = pdfkit.from_string(template, False, configuration=config_path)

            response = make_response(invoice_pdf)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % "invoice"
            Logs.save_log("Invoice Downloaded Successfully", session["user_type"], session["user"])
            return response
        else:
            return redirect(url_for("login"))
    # =============================== /download-invoice Route Ends Here ===============================

    # =============================== /view-invoices Route View ===============================
    @staticmethod
    @app.route("/view-invoices", methods=["GET", "POST"])
    def view_invoices():
        if "user" in session and session["user_type"] == "user":
            user_data = Users.get_user_data(session["user"])
            page_data = {"page_title": "View Invoices", "page_heading": "Your Invoices"}
            all_invoices = Invoices.get_this_user_invoices(session["user"])
            return render_template("view_invoices.html", page_data=page_data, user_data=user_data,
                                   all_invoices=all_invoices)
        else:
            return redirect(url_for("login"))
    # =============================== /view-invoices Route View Ends Here ===============================

    # =============================== /view-brands Route View ===============================
    @staticmethod
    @app.route("/view-brands", methods=["GET", "POST"])
    def view_brands():
        if "user" in session and session["user_type"] == "user":
            user_data = Users.get_user_data(session["user"])
            page_data = {"page_title": "View Brands", "page_heading": "View Brands"}
            all_brands = Brands.get_all_brands()
            return render_template("view_brands.html", all_brands=all_brands, page_data=page_data, user_data=user_data)
        else:
            return redirect(url_for("login"))
    # =============================== /view-brands Route View Ends Here ===============================

    # =============================== /view-products Route View ===============================
    @staticmethod
    @app.route("/view-products", methods=["GET", "POST"])
    def view_products():
        if "user" in session and session["user_type"] == "user":
            user_data = Users.get_user_data(session["user"])
            page_data = {"page_title": "View Products", "page_heading": "View Products"}
            all_products = Products.get_all_products()
            return render_template("view_products.html", all_products=all_products,
                                   page_data=page_data, user_data=user_data)
        else:
            return redirect(url_for("login"))
    # =============================== /view-products Route View Ends Here ===============================

    # =============================== /view-members Route View ===============================
    @staticmethod
    @app.route("/view-members", methods=["GET", "POST"])
    def view_members():
        if "user" in session and session["user_type"] == "user":
            user_data = Users.get_user_data(session["user"])
            page_data = {"page_title": "View Members", "page_heading": "View Members"}
            members_data = Members.get_all_members_data()
            return render_template("view_members.html", members_data=members_data,
                                   page_data=page_data, user_data=user_data)
        else:
            return redirect(url_for("login"))
    # =============================== /view-members Route View Ends Here ===============================

    # =============================== /forecasting Route View ===============================
    @staticmethod
    @app.route("/forecasting", methods=["GET", "POST"])
    def forecasting():
        if "user" in session and session["user_type"] == "admin":
            page_data = {"page_title": "Sales Forecasting", "page_heading": "Sales Forecasting"}
            admin_data = Admins.get_admin_data(session["user"])
            stats = generate_forecast_data()
            if stats is False:
                flash("We Cannot Perform Forecasting On Data Yet, Please Make Sure You Have At Least 10 Days Data",
                      category="warning")
                return redirect(url_for("admin_dashboard", admin_id=session["user"]))
            else:
                forecast_data = ForecastData.get_by_date_forecast()
                all_forecast_data = ForecastData.get_all_data()
                Logs.save_log("Next 15 Days Sales Forecast Performed", session["user_type"], session["user"])
                return render_template("forecast.html", page_data=page_data, admin_data=admin_data,
                                       forecast_data=forecast_data, all_forecast_data=all_forecast_data,
                                       all_stats=stats)
        else:
            return redirect(url_for("login"))
    # =============================== /forecasting Route View Ends Here ===============================


# =============================== *****Running The Application***** ===============================
if __name__ == '__main__':
    app.run(host="127.0.0.1", port="5000", debug=True)
# =================================================================================================
