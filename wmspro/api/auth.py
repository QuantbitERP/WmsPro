import frappe

@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    login_manager = frappe.auth.LoginManager()
    login_manager.authenticate(user=usr, pwd=pwd)
    login_manager.post_login()

    if frappe.response['message'] == 'Logged In':
        frappe.response['user'] = login_manager.user
        
    return frappe.response

@frappe.whitelist()
def get_current_user():
    return frappe.session.user

@frappe.whitelist()
def logout():
    frappe.local.login_manager.logout()
    frappe.db.commit()
    return {"message": "Logged Out"}
