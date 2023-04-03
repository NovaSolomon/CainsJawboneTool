import sqlite3
from termcolor import colored

colors = {
    "User-Prompt": 'magenta',
    "Dev-Prompt": 'green',
    "Input-Prompt": 'cyan',
    "Content-Output": 'white',
    "Structure-Output": 'yellow',
    "Error": 'red',
}

def print_e(text):
    print(colored(text, colors["Error"]))

def output(category, value, newline = False):
    e = ' '
    if newline:
        e = '\n'
    print(colored(category, colors["Structure-Output"]), end=e)
    print(colored(value.replace('$', '"'), colors["Content-Output"]))

def input_prompt(text, newline = False, limit = 2000):
    e = ' '
    if newline:
        e = '\n'
    print(colored(text, colors["Input-Prompt"]), end=e)
    i = input().replace('"', '$')
    while len(i) > limit:
        print_e(f"Must be {limit} characters or less")
        print(colored(text, colors["Input-Prompt"]), end=e)
        i = input().replace('"', '$')
    return i

def print_s(text, newline = True):
    e = ''
    if newline: e = "\n"
    print(colored(text, colors["Structure-Output"]), end=e)

def check_args(cmd, cmd_len, arg_len) -> bool:
    n = len(cmd) - cmd_len
    if n == arg_len: return True
    if arg_len == 1:
        print_e(f"Expected 1 argument, but received {n}")    
    else:
        print_e(f"Expected {arg_len} arguments, but received {n}")
    return False

def hug(text, wrapper = '"'):
    return wrapper + text + wrapper

class Terminal:
    user_commands = None

    def __init__(self, db_path) -> None:
        self.db_con = sqlite3.connect(db_path)
        self.db_cur = self.db_con.cursor()
        self.mode = "User"
        self.done = False

    def serve(self):
        while not self.done:
            self.get_command()
            self.match_and_execute()

    def get_command(self):
        if self.mode == "User":
            print(colored(">>>", colors["User-Prompt"]), end=' ')
        elif self.mode == "Dev":
            print(colored("<?>", colors["Dev-Prompt"]), end=' ')
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
                            print_e("No quotes allowed within words")
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
                            print_e("There must be a space after a closing quote")
                            return
        if q:
            print_e("Unclosed quotes!")
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
        print_e("Command not recognized. Maybe you forgot an argument?\nUse 'help' for directions")
        print()

    #Dev Commands
    def dev_new_page(self, cmd):
        if not check_args(cmd, 2, 0): return
        c = self.db_cur.execute(
            "SELECT COUNT(bookpage) FROM pages;"
            ).fetchone()[0]
        if c < 100:
            page_nr = c + 1
            txt = input_prompt(f"Enter Text for page {page_nr}:", True)
            if txt == '':
                return
            self.db_cur.execute(
                f'INSERT INTO pages (booktext) VALUES ("{txt}");'
                )
            self.db_con.commit()
        else:
            print_e("No room for additional pages!")

    def dev_edit_page(self, cmd):
        if not check_args(cmd, 2, 1): return
        page = 0
        try:
            page = int(cmd[2])
        except:
            print_e("Argument must be integer between 1 and 100")
            return
        if page > self.db_cur.execute(
            "SELECT COUNT(bookpage) FROM pages;"
            ).fetchone()[0] or page <= 0:
            print_e("Requested page does not exist")
            return
        crnt_text = self.db_cur.execute(
            f"SELECT booktext FROM pages WHERE bookpage={page};"
            ).fetchone()[0]
        output(f"Booktext page {page}:", crnt_text, True)
        new_text = input_prompt("Enter new text:", True)
        if new_text == '': return
        self.db_cur.execute(
            f'UPDATE pages SET booktext="{new_text}" WHERE bookpage={page};'
        )
        self.db_con.commit()
        

    def dev_delete_last_page(self, cmd):
        if not check_args(cmd, 3, 0): return
        last_page = self.db_cur.execute(
            "SELECT COUNT(bookpage) FROM pages;"
        ).fetchone()[0]
        if last_page == 0:
            print_e("No Pages to delete")
            return
        ans = ''
        while ans not in ('Y', 'n'):
            ans = input_prompt(f"Are you sure you want to delete page {last_page}? (Y/n)")
        if ans == 'n': return
        self.db_cur.execute(
            f"DELETE FROM pages WHERE bookpage={last_page};"
        )
        self.db_con.commit()

    def dev_exit(self, cmd):
        if not check_args(cmd, 3, 0): return
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
        if not check_args(cmd, 2, 0): return
        self.mode = "Dev"
        print_e("Warning: Only use dev mode if you're absolutely sure of what you're doing."+
                "\nIf not, you can leave with 'exit dev mode'")

    def exit_cli(self, cmd):
        if not check_args(cmd, 1, 0): return
        self.done = True

    def back_up_db(self, cmd):
        pass

    def list_backups(self, cmd):
        pass

    def save_state_as_backup(self, cmd):
        pass

    def help(self, cmd):
        if not check_args(cmd, 1, 0): return
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
        if not check_args(cmd, 2, 0): return False
        name = input_prompt("Name:", limit=30)
        if name == '': return False
        if 0 < self.db_cur.execute(
            f'SELECT COUNT(*) FROM people WHERE name="{name}";'
        ).fetchone()[0]:
            print_e("Person already exists")
            return False
        self.db_cur.execute(
            f'INSERT INTO people (name) VALUES ("{name}");'
        )
        self.db_con.commit()
        return True

    def new_group(self, cmd):
        if not check_args(cmd, 2, 0): return False
        name = input_prompt("Group name:", limit=30)
        if name == '': return False
        if 0 < self.db_cur.execute(
            f'SELECT COUNT(*) FROM groups WHERE name="{name}";'
        ).fetchone()[0]:
            print_e("Group already exists")
            return False
        self.db_cur.execute(
            f'INSERT INTO groups (name) VALUES ("{name}");'
        )
        self.db_con.commit()
        return True

    def new_location(self, cmd):
        if not check_args(cmd, 2, 0): return False
        name = input_prompt("Name:", limit=50)
        if name == '': return False
        if 0 < self.db_cur.execute(
            f'SELECT COUNT(*) FROM locations WHERE name="{name}";'
        ).fetchone()[0]:
            print_e("Location already exists")
            return False
        level = input_prompt("Level:", limit=30)
        if level == '':
            self.db_cur.execute(
                f'INSERT INTO locations (name) VALUES ("{name}");'
            )
        else:
            self.db_cur.execute(
                f'INSERT INTO locations (name, level) VALUES ("{name}", "{level}");'
            )
        self.db_con.commit()
        return True

    def new_time(self, cmd):
        if not check_args(cmd, 2, 0): return False
        name = input_prompt("Name:", limit=50)
        if name == '': return False
        if 0 < self.db_cur.execute(
            f'SELECT COUNT(*) FROM times WHERE name="{name}";'
        ).fetchone()[0]:
            print_e("Time already exists")
            return False
        level = input_prompt("Level:", limit=30)
        if level == '':
            self.db_cur.execute(
                f'INSERT INTO times (name) VALUES ("{name}");'
            )
        else:
            self.db_cur.execute(
                f'INSERT INTO times (name, level) VALUES ("{name}", "{level}");'
            )
        self.db_con.commit()
        return True



    def add_new_person_to_page(self, cmd):
        if not check_args(cmd, 5, 1): return
        page = 0
        try:
            page = int(cmd[5])
        except:
            print_e("Argument has to be an integer")
            return
        if page < 1 or page > 100:
            print_e("Bookpage must be between 1 and 100")
            return
        print_s("New person")
        if not self.new_person(("new", "person")): return
        self.db_cur.execute(
            f"""INSERT INTO pages_people (page_number, person_id)
            VALUES ({page}, (SELECT MAX(id) FROM people));"""
        )
        self.db_con.commit()


    def add_new_location_to_page(self, cmd):
        if not check_args(cmd, 5, 1): return
        page = 0
        try:
            page = int(cmd[5])
        except:
            print_e("Argument has to be an integer")
            return
        if page < 1 or page > 100:
            print_e("Bookpage must be between 1 and 100")
            return
        print_s("New location")
        if not self.new_location(("new", "location")): return
        self.db_cur.execute(
            f"""INSERT INTO pages_locations (page_number, person_id)
            VALUES ({page}, (SELECT MAX(id) FROM locations));"""
        )
        self.db_con.commit()

    def add_new_time_to_page(self, cmd):
        if not check_args(cmd, 5, 1): return
        page = 0
        try:
            page = int(cmd[5])
        except:
            print_e("Argument has to be an integer")
            return
        if page < 1 or page > 100:
            print_e("Bookpage must be between 1 and 100")
            return
        print_s("New time")
        if not self.new_time(("new", "time")): return
        self.db_cur.execute(
            f"""INSERT INTO pages_times (page_number, time_id)
            VALUES ({page}, (SELECT MAX(id) FROM times));"""
        )
        self.db_con.commit()

    def add_pages_to_new_group(self, cmd):
        if not check_args(cmd, 5, 0): return
        pages = []
        ans = 'tmp'
        while ans != '':
            ans = input_prompt("Page number:")
            page = 0
            try:
                page = int(ans)
            except:
                if ans != '': print_e("Must be an integer")
                continue
            if page < 1 or page > 100:
                print_e("Must be between 1 and 100")
                continue
            if page in pages:
                print_e("Page already added")
                continue
            pages.append(page)
        print()
        print_s("New group")
        if not self.new_group(("new", "group")): return
        for page in pages:
            self.db_cur.execute()

    def add_page_to_new_group(self, cmd):
        if not check_args(cmd, 6, 0): return
        page = 0
        try:
            page = int(cmd[2])
        except:
            print_e("Bookpage must be an integer")
            return
        if page < 1 or page > 100:
            print_e("Bookpage must be between 1 and 100")
            return
        print_s("New Group")
        if not self.new_group(("new", "group")): return
        self.db_cur.execute(
            f"""INSERT INTO groups_pages (group_id, page_number)
            VALUES ((SELECT MAX(*) FROM groups), {page});"""
        )
        self.db_con.commit()

    def add_nickname(self, cmd):
        if not check_args(cmd, 3, 1): return
        name = cmd[3]
        id = self.db_cur.execute(
            f"""SELECT id FROM people
            WHERE name="{name}";"""
        ).fetchone()
        try:
            id = id[0]
        except:
            print_e("Person doesn't exist")
            return
        nickname = input_prompt("Nickname:", limit=30)
        if nickname == '': return
        self.db_cur.execute(
            f"""INSERT INTO nicknames (name, person_id)
            VALUES ("{nickname}", {id});"""
        )
        self.db_con.commit()

    def add_note(self, cmd):
        if not check_args(cmd, 3, 2): return
        category = cmd[3]
        ident = cmd[4]
        match category:
            case "group":
                if self.db_cur.execute(
                    f"""SELECT COUNT(*) FROM groups
                    WHERE name="{ident}";"""
                ).fetchone()[0] == 0:
                    print_e("Group doesn't exist")
                    return
                note = input_prompt("Note text:", True)
                if note == "": return
                id = self.db_cur.execute(
                    f"""SELECT id FROM groups
                    WHERE name="{ident}";"""
                ).fetchone()[0]
                self.db_cur.execute(
                    f"""INSERT INTO notes (object, note_text, object_id)
                    VALUES ("group", "{note}", {id});"""
                )
                self.db_con.commit()
            case "person":
                if self.db_cur.execute(
                    f"""SELECT COUNT(*) FROM people
                    WHERE name="{ident}";"""
                ).fetchone()[0] == 0:
                    print_e("Person doesn't exist")
                    return
                note = input_prompt("Note text:", True)
                if note == "": return
                id = self.db_cur.execute(
                    f"""SELECT id FROM people
                    WHERE name="{ident}";"""
                ).fetchone()[0]
                self.db_cur.execute(
                    f"""INSERT INTO notes (object, note_text, object_id)
                    VALUES ("person", "{note}", {id});"""
                )
                self.db_con.commit()
            case "location" | "time":
                table = category + "s"
                if self.db_cur.execute(
                    f"""SELECT COUNT(*) FROM {table}
                    WHERE name="{ident}";"""
                ).fetchone()[0] == 0:
                    print_e(f"{category} doesn't exist")
                    return
                note = input_prompt("Note text:", True)
                if note == "": return
                id = self.db_cur.execute(
                    f"""SELECT id FROM {table}
                    WHERE name="{ident}";"""
                ).fetchone()[0]
                self.db_cur.execute(
                    f"""INSERT INTO notes (object, note_text, object_id)
                    VALUES ("{category}", "{note}", {id});"""
                )
                self.db_con.commit()
            case "page":
                id = 0
                try:
                    id = int(ident)
                except:
                    print_e("Page number must be integer")
                    return
                if id < 1 or 100 < id:
                    print_e("Page number must be between 1 and 100")
                    return
                note = input_prompt("Note text:", True)
                if note == "": return
                self.db_cur.execute(
                    f"""INSERT INTO notes (object, note_text, object_id)
                    VALUES ("page", "{note}", {id});"""
                )
                self.db_con.commit()
            case _:
                print_e("Category doesn't exist")


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