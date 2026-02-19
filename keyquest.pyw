#!python3.9

try:
    from modules.keyquest_app import main
except Exception as e:
    try:
        from modules import error_logging

        error_logging.log_exception(e)
    except Exception:
        pass
    raise


if __name__ == "__main__":
    main()
