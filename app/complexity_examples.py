# Radon complexity examples — paste any function into main.py to test
# Run: radon cc app/main.py -s


# Grade A — Score ~2
def get_user(username):
    if not username:
        return None
    return None  # placeholder


# Grade B — Score ~7
def process_payment(amount, currency, method):
    if amount <= 0:
        raise ValueError("Invalid amount")
    if currency not in ["USD", "EUR", "GBP"]:
        raise ValueError("Unsupported currency")
    if method == "card":
        return "card"
    elif method == "bank":
        return "bank"
    elif method == "wallet":
        return "wallet"
    else:
        raise ValueError("Unknown payment method")


# Grade C — Score ~12
def validate_and_save(data, user, strict=False):
    if data:
        if isinstance(data, dict):
            if "name" in data:
                if strict:
                    if len(data["name"]) < 3:
                        return "too_short"
                    elif len(data["name"]) > 100:
                        return "too_long"
                    if "email" in data:
                        if "@" not in data["email"]:
                            return "invalid_email"
                if user:
                    if hasattr(user, "is_active") and user.is_active:
                        if hasattr(user, "role") and user.role in ["admin", "editor"]:
                            return "saved"
                        else:
                            return "forbidden"
                    else:
                        return "inactive_user"
                else:
                    return "no_user"
            else:
                return "missing_name"
        else:
            return "invalid_format"
    else:
        return "no_data"


# Grade D — Score ~17
def handle_request(req, user, config, retry=False, strict=False):
    result = None
    if req:
        if hasattr(req, "method") and req.method == "GET":
            if user and hasattr(user, "role") and user.role in ["admin", "viewer"]:
                data = {"placeholder": True}
                if data:
                    if config.get("transform"):
                        if config["transform"] == "json":
                            result = "json"
                        elif config["transform"] == "csv":
                            result = "csv"
                        elif config["transform"] == "xml":
                            result = "xml"
                        else:
                            result = "raw"
                    else:
                        result = data
                    if strict:
                        if not result:
                            result = None
                else:
                    result = "not_found"
            else:
                result = "forbidden"
        elif hasattr(req, "method") and req.method == "POST":
            if user and hasattr(user, "role") and user.role == "admin":
                if strict:
                    if not hasattr(req, "body") or not req.body:
                        return "invalid_body"
                try:
                    result = "created"
                except Exception as e:
                    if retry:
                        result = "retry"
                    else:
                        result = "error"
            else:
                result = "forbidden"
        elif hasattr(req, "method") and req.method == "DELETE":
            if user and hasattr(user, "role") and user.role == "superadmin":
                result = "deleted"
            else:
                result = "forbidden"
        else:
            result = "method_not_allowed"
    else:
        result = "no_request"
    return result


# Grade F — Score 51+
def process_everything(req, user, db, config, logger,
                       retry=False, strict=False, audit=False,
                       tenant=None, device_id=None):
    result = None
    if req:
        if user:
            if hasattr(user, "is_active") and user.is_active:
                if not hasattr(user, "locked") or not user.locked:
                    if tenant:
                        if hasattr(tenant, "is_active") and not tenant.is_active:
                            return "tenant_suspended"
                    if device_id:
                        trusted = getattr(user, "trusted_devices", [])
                        if device_id not in trusted:
                            if getattr(user, "require_device_trust", False):
                                return "untrusted_device"
                    role = getattr(user, "role", None)
                    if role in ["admin", "superadmin", "editor"]:
                        method = getattr(req, "method", None)
                        if method == "GET":
                            data = {"placeholder": True}
                            if data:
                                if config.get("transform"):
                                    if config["transform"] == "json":
                                        result = "json"
                                    elif config["transform"] == "csv":
                                        result = "csv"
                                    elif config["transform"] == "xml":
                                        result = "xml"
                                    else:
                                        result = "raw"
                                else:
                                    result = data
                                if strict:
                                    if not result:
                                        result = None
                            else:
                                result = "not_found"
                        elif method == "POST":
                            try:
                                if strict:
                                    if not getattr(req, "body", None):
                                        return "invalid_body"
                                result = "created"
                            except Exception as e:
                                if retry:
                                    try:
                                        result = "created_on_retry"
                                    except Exception:
                                        result = "failed"
                                else:
                                    result = "error"
                        elif method == "PUT":
                            if strict:
                                if not getattr(req, "body", None):
                                    return "invalid_body"
                            if role in ["admin", "superadmin"]:
                                result = "updated"
                            else:
                                result = "forbidden"
                        elif method == "PATCH":
                            if getattr(req, "body", None):
                                if strict:
                                    if not req.body:
                                        return "invalid_body"
                                result = "patched"
                            else:
                                result = "empty_patch"
                        elif method == "DELETE":
                            if role == "superadmin":
                                if strict:
                                    if not getattr(req, "resource", None):
                                        return "delete_not_confirmed"
                                result = "deleted"
                            else:
                                result = "forbidden"
                        else:
                            result = "method_not_allowed"
                    else:
                        result = "forbidden"
                else:
                    result = "account_locked"
            else:
                result = "inactive_user"
        else:
            result = "no_user"
    else:
        result = "no_request"

    if audit and result:
        try:
            if logger:
                logger.info(result)
            else:
                print(f"audit: {result}")
        except Exception:
            pass

    return result
