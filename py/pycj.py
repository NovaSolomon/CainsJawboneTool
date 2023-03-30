class Terminal:
    user_commands = None

    def __init__(self, db_path = "./data.db") -> None:
        self.db_path = db_path
        self.mode = "User"
        self.done = False

    def serve(self):
        while not self.done:
            self.get_command()
            self.match_and_execute()

    def get_command(self):
        if self.mode == "User":
            print(">>>", end=' ')
        elif self.mode == "Dev":
            print("<?>", end=' ')
        self.cmd = input()

    def match_and_execute(self):
        if self.mode == "User":
            reg = self.user_commands
        elif self.mode == "Dev":
            reg = self.dev_commands

        cmd = []
        l = 0
        w, q = (False, False)
        qp = False
        self.cmd += ' '
        for i, c in enumerate(self.cmd):
            match (w, q):
                case (_, True):
                    if c == '"':
                        w, q = (False, False)
                        qp = True
                        cmd.append(self.cmd[l:i])
                case (True, False):
                    match c:
                        case '"':
                            print("No quotes allowed within words")
                            return
                        case ' ':
                            w = False
                            cmd.append(self.cmd[l:i])
                case (False, False):
                    if not qp:
                        if c == '"':
                            q, w = (True, True)
                            l = i + 1
                        elif c != ' ':
                            w = True
                            l = i
                    else:
                        if c == ' ':
                            qp = False
                        else:
                            print("There must be a space after a closing quote")
                            return
        if q:
            print("Unclosed quotes!")
            return
        matched = False
        length = len(cmd)
        for k in reg.keys():
            if length < len(k): continue
            matched = True
            for i, s in enumerate(k):
                if s != '_' and s != cmd[i]:
                    matched = False
                    break
            if matched:
                reg[k](self, cmd)
                break
        if not matched:
            self.cmd_not_found()
        

    def cmd_not_found(self):
        print("Command not recognized. Use 'help' for directions")
        print()

    #Dev Commands
    def dev_new_page(self, cmd):
        print(1)
        print(cmd)
        print(self.db_path)

    def dev_edit_page(self, cmd):
        print(2)
        print(cmd)

    def dev_delete_last_page(self, cmd):
        print(3)
        print(cmd)

    def dev_exit(self, cmd):
        self.mode = "User"

    dev_commands = {
        ("new", "page"): dev_new_page,
        ("edit", "page", "_"): dev_edit_page,
        ("delete", "last", "page"): dev_delete_last_page,
        ("exit", "dev", "mode"): dev_exit,
    }



    #User Commands
    ##System Commands
    def enter_dev_mode(self, cmd):
        self.mode = "Dev"

    def exit_cli(self, cmd):
        self.done = True

    def back_up_db(self, cmd):
        pass

    def list_backups(self, cmd):
        pass

    def save_state_as_backup(self, cmd):
        pass

    def help(self, cmd = None):
        f = open("help-message.txt", 'r')
        f_content = f.read()
        print(f_content)
        f.close()


    ##Read/list information
    def show_page(self, cmd):
        pass

    def show_person(self, cmd):
        pass

    def show_location(self, cmd):
        pass

    def show_time(self, cmd):
        pass

    def show_group(self, cmd):
        pass


    def list_relations(self, cmd):
        pass

    def list_people(self, cmd):
        pass

    def list_groups(self, cmd):
        pass

    def list_locations(self, cmd):
        pass

    def list_times(self, cmd):
        pass


    def list_pages_with(self, cmd):
        pass

    def list_pages_where(self, cmd):
        pass


    ##Make new entities
    def new_person(self, cmd):
        pass

    def new_group(self, cmd):
        pass

    def new_location(self, cmd):
        pass

    def new_time(self, cmd):
        pass


    def add_new_person_to_page(self, cmd):
        pass

    def add_new_location_to_page(self, cmd):
        pass


    user_commands = {
        ("dev", "mode",): enter_dev_mode,
        ("exit",): exit_cli,
        ("back", "up", "db",): back_up_db,
        ("list", "backups",): list_backups,
        ("save", "state", "as", "backup",): save_state_as_backup,
        ("help",): help,
    }