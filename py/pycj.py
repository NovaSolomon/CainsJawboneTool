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
        print("Command not recognized. Maybe you forgot an argument?\nUse 'help' for directions")
        print()

    #Dev Commands
    def dev_new_page(self, cmd):
        pass

    def dev_edit_page(self, cmd):
        pass

    def dev_delete_last_page(self, cmd):
        pass

    def dev_exit(self, cmd):
        self.mode = "User"

    dev_commands = {
        ("new", "page"): dev_new_page,
        ("edit", "page"): dev_edit_page,
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

    def add_new_time_to_page(self, cmd):
        pass

    def add_pages_to_new_group(self, cmd):
        pass

    def add_page_to_new_group(self, cmd):
        pass

    def add_nickname(self, cmd):
        pass

    def add_note(self, cmd):
        pass


    ##Link existing entities
    def add_pages_to_group(self, cmd):
        pass

    def add_page_to_group(self, cmd):
        pass


    def link_person_to_page(self, cmd):
        pass

    def link_location_to_page(self, cmd):
        pass

    def link_time_to_page(self, cmd):
        pass


    def solved_a_murder(self, cmd):
        pass


    def order_groups(self, cmd):
        pass

    def order_pages(self, cmd):
        pass


    ##Unlink existing entities
    def remove_pages_from_group(self, cmd):
        pass


    def remove_name_from_page(self, cmd):
        pass

    def remove_location_from_page(self, cmd):
        pass

    def remove_time_from_page(self, cmd):
        pass


    def edit_killer_registry(self, cmd):
        pass


    def remove_group_relations(self, cmd):
        pass

    def remove_page_relations(self, cmd):
        pass


    ##Change attributes
    def edit_page(self, cmd):
        pass

    def edit_location(self, cmd):
        pass

    def edit_time(self, cmd):
        pass


    ##Delete entities
    def remove_person(self, cmd):
        pass

    def remove_group(self, cmd):
        pass

    def remove_location(self, cmd):
        pass

    def remove_time(self, cmd):
        pass


    ##Unify two entities
    def merge_groups(self, cmd):
        pass

    def merge_people(self, cmd):
        pass

    def merge_locations(self, cmd):
        pass

    def merge_times(self, cmd):
        pass


    ##Find appearances of strings
    def scan_for_text(self, cmd):
        pass


    ##Miscellaneous
    def calculate_possibilities(self, cmd):
        pass


    user_commands = {
        ("dev", "mode",): enter_dev_mode,
        ("exit",): exit_cli,
        ("back", "up", "db",): back_up_db,
        ("list", "backups",): list_backups,
        ("save", "state", "as", "backup",): save_state_as_backup,
        ("help",): help,


        ("show", "page"): show_page,
        ("show", "person"): show_person,
        ("show", "location"): show_location,
        ("show", "time"): show_time,
        ("show", "group"): show_group,

        ("list", "relations"): list_relations,
        ("list", "people"): list_people,
        ("list", "groups"): list_groups,
        ("list", "locations"): list_locations,
        ("list", "times"): list_times,

        ("list", "pages", "with"): list_pages_with,
        ("list", "pages", "where"): list_pages_where,


        ("new", "person"): new_person,
        ("new", "group"): new_group,
        ("new", "location"): new_location,
        ("new", "time"): new_time,

        ("add", "new", "person", "to", "page"): add_new_person_to_page,
        ("add", "new", "location", "to", "page"): add_new_location_to_page,
        ("add", "new", "time", "to", "page"): add_new_time_to_page,
        ("add", "pages", "to", "new", "group"): add_pages_to_new_group,
        ("add", "page", "_", "to", "new", "group"): add_page_to_new_group,
        ("add", "nickname", "to"): add_nickname,
        ("add", "note", "to"): add_note,


        ("add", "pages", "to", "group"): add_pages_to_group,
        ("add", "page", "_", "to", "group"): add_page_to_group,

        ("link", "_", "to", "page"): link_person_to_page,
        ("link", "location", "_", "to", "page"): link_location_to_page,
        ("link", "time", "_", "to", "page"): link_time_to_page,

        ("solved", "a", "murder"): solved_a_murder,

        ("order", "_", "before"): order_groups,
        ("oder", "page", "_", "before"): order_pages,


        ("remove", "pages", "from", "group"): remove_pages_from_group,
        
        ("remove", "person", "from", "page"): remove_person,
        ("remove", "location", "from", "page"): remove_location,
        ("remove", "time", "from", "page"): remove_time,

        ("edit", "killer", "registry"): edit_killer_registry,

        ("remove", "group", "relations"): remove_group_relations,
        ("remove", "page", "relations"): remove_page_relations,


        ("edit", "page"): edit_page,
        ("edit", "location"): edit_location,
        ("edit", "time"): edit_time,


        ("remove", "person"): remove_person,
        ("remove", "group"): remove_group,
        ("remove", "location"): remove_location,
        ("remove", "time"): remove_time,


        ("merge", "groups"): merge_groups,
        ("merge", "people"): merge_people,
        ("merge", "locations"): merge_locations,
        ("merge", "times"): merge_times,


        ("scan",): scan_for_text,


        ("calculate", "possibilities"): calculate_possibilities,
    }