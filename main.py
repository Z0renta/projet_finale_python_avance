from ui.app_window import Application
        
if __name__ == '__main__':
    app = Application()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()