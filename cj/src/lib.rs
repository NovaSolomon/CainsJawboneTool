use std::fmt::Error;
use std::io::Write;
use std::io;
use sqlite::{self, Statement};

enum TerminalMode {
    DevMode,
    UserMode,
}

#[derive(PartialEq, Debug)]
enum ParsingError {
    UnclosedQuotes,
    QuotesInWords,
    NoSpaceAfterQuote,
    EmptyCommand,
}

pub struct Terminal<> {
    input: io::Stdin,
    output: io::Stdout,
    mode: TerminalMode,
    db_connection: sqlite::Connection,
    cmd: Option<Vec<String>>,
    exit: bool,
}

impl Terminal {
    pub fn new(input: io::Stdin, output: io::Stdout , db_path: &str) -> Result<Terminal, Error> {
        Ok(Terminal {
            input,
            output,
            mode: TerminalMode::UserMode,
            db_connection: sqlite::open(db_path).expect("Error finding db"),
            cmd: None,
            exit: false,
        })
    }

    pub fn serve(mut self) {
        while !self.exit {
            self = self.read_command();
            self = self.execute_command();
        }
    }

    fn toggle_mode(mut self) -> Self {
        match self.mode {
            TerminalMode::DevMode => { self.mode = TerminalMode::UserMode; },
            TerminalMode::UserMode => { self.mode = TerminalMode::DevMode; },
        }
        self
    }

    fn read_command(mut self) -> Self {
        match self.mode {
            TerminalMode::DevMode => { write!(self.output, "\n<?> ").expect("Error outputting Text"); },
            TerminalMode::UserMode => { write!(self.output, "\n>>> ").expect("Error outputting text"); },
        }
        self.output.flush().expect("Flush failed");
        let mut cmd_text = String::new();
        if let Ok(_) =  self.input.read_line(&mut cmd_text) {
            cmd_text = String::from(cmd_text.trim());
            match Terminal::str_to_vec(cmd_text) {
                Ok(v) => self.cmd = Some(v),
                Err(e) => {
                    match e {
                        ParsingError::QuotesInWords => writeln!(self.output, "No quotes allowed within a word").unwrap(),
                        ParsingError::UnclosedQuotes => writeln!(self.output, "Unclosed quotes!").unwrap(),
                        ParsingError::NoSpaceAfterQuote => writeln!(self.output, "After closing a quote, leave a space")
                        .unwrap(),
                        _ => (),
                    };
                    self.cmd = None },
            }
        } else {
            self.cmd = None;
        }
        self
    }

    fn str_to_vec(mut s: String) -> Result<Vec<String>, ParsingError> {
        if s.as_str() == "" {return Err(ParsingError::EmptyCommand);}
        s.push(' ');
        let mut res = Vec::new();
        let mut l = 0;
        let (mut w, mut q, mut qp) = (false, false, false);
        for (i, c) in s.chars().enumerate() {
            match (w, q) {
                (_, true) => {
                    if c == '"' {
                        w = false; q = false; qp = true;
                        res.push(String::from(&s[l..i]));
                    }
                },
                (true, false) => {
                    match c {
                        '"' => return Err(ParsingError::QuotesInWords),
                        ' ' => {
                            w = false;
                            res.push(String::from(&s[l..i]));
                        },
                        _ => (),
                    }
                }
                (false, false) => if qp == false {
                    if c == '"' {
                        q = true;
                        w = true;
                        l = i + 1;
                    } else if c != ' ' {
                        w = true;
                        l = i;
                    }
                } else {
                    if c == ' ' { qp = false; }
                    else { return Err(ParsingError::NoSpaceAfterQuote); }
                },
            }
        }
        if q == true {
            Err(ParsingError::UnclosedQuotes)
        } else {
            Ok(res)
        }
    }

    fn execute_command(mut self) -> Self {
        if self.cmd == None {return self};
        match self.mode {
            TerminalMode::DevMode => {
                match self.cmd.clone().unwrap()[0].as_str() {
                    "new" => { self = self.dev_new_page() },
                    "edit" => { self = self.dev_edit_page() },
                    "delete" => { self = self.dev_delete_page() },
                    "exit" => { self = self.dev_exit() },
                    _ => (),
                }
            },
            TerminalMode::UserMode => {
                match self.cmd.clone().unwrap()[0].as_str() {
                    "dev" => { self = self.enter_dev_mode() },
                    "exit" => { self = self.exit_terminal() },
                    _ => (),
                }
            },
        }
        self
    }

    pub fn destroy(self) {}

    fn user_error(mut self, correct_form: &str) -> Self {
        write!(self.output, "Did you mean '{}'?\n    Use 'help' for a list of commands.\n", correct_form).unwrap();
        self
    } 

    fn custom_user_error(mut self, message: &str) -> Self {
        write!(self.output, "{}\n    Use 'help' for a list of commands.\n", message).unwrap();
        self
    } 

    fn dev_new_page(mut self) -> Self {
        if self.cmd.clone().unwrap() == vec!["new", "page"] {
            writeln!(self.output, "Please enter page text:").unwrap();
            let mut page_text = String::new();
            self.input.read_line(&mut page_text).unwrap();
            page_text = page_text.replace('"', "$");
            let query = format!(r#"INSERT INTO pages (booktext) VALUES ("{}");"#, page_text);
            self.db_connection.execute(query).unwrap();
        } else {
            self = self.user_error("new page");
        }
        self
    }

    fn dev_edit_page(mut self) -> Self {
        let v = self.cmd.clone().unwrap();
        if v.len() != 3 {
            self = self.user_error("edit page {page number}");
            return self;
        }
        match (v[0].as_str(), v[1].as_str(), v[2].as_str()) {
            ("edit", "page", s) => match s.parse() {
                Ok(i) => {
                    if 0 < i && i <= 100 {
                        // Still has to be done !!!
                        let query = format!("SELECT COUNT(bookpage) FROM pages WHERE bookpage={};", i);
                        let statement = self.db_connection.prepare(query).unwrap();
                        let c = statement.into_iter().next().unwrap().unwrap().read::<i64,_>("COUNT(bookpage)");
                        if c == 1 {
                            let statement = self.db_connection.prepare(format!("SELECT booktext FROM pages WHERE bookpage={};", i)).unwrap();
                            //let crnt_text = statement.into_iter().next().unwrap().unwrap().read::<&str,_>("booktext");
                            let mut crnt_text = String::new();
                            for row in statement.into_iter().map(|r| r.unwrap()) {
                                crnt_text = row.read::<String,&str>("booktext");
                                break;
                            }
                            writeln!(self.output, "Current Text:\n{}", crnt_text).unwrap();
                        } else {
                            self = self.custom_user_error("Page not yet in database");
                        }
                    } else {
                        self = self.custom_user_error("Page number must be between 0 and 100")
                    }

                },
                Err(_) => self = self.custom_user_error("Bookpage must be an integer"),
            },
            _ => self = self.user_error("edit page {page number}"),
        };
        self
    }

    fn dev_delete_page(mut self) -> Self {
        self
    }

    fn dev_exit(mut self) -> Self {
        if self.cmd.clone().unwrap() == vec!["exit", "dev", "mode"] {
            self = self.toggle_mode();
        } else {
            self = self.user_error("exit dev mode");
        }
        self
    }

    fn enter_dev_mode(mut self) -> Self {
        if self.cmd.clone().unwrap() == vec!["dev", "mode"] {
            self = self.toggle_mode();
        } else {
            self = self.user_error("dev mode");
        }
        self
    }

    fn exit_terminal(mut self) -> Self {
        if self.cmd.clone().unwrap().len() == 1 {
            self.exit = true;
        } else {
            self = self.user_error("exit");
        }
        self
    }




}