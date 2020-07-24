
if __name__ == '__main__':
    import sys
    from CAMOnion.app import Controller
    app = Controller(sys.argv)
    sys.exit(app.launch())

