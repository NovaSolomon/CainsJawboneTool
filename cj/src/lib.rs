use std::fmt::Error;
use std::io::Write;
use std::io;
use sqlite;

enum TerminalMode {
    _DevMode,
    UserMode,
}

#[derive(PartialEq, Debug)]
enum ParsingError {
    UnclosedQuotes,
    QuotesInWords,
    NoSpaceAfterQuote,
}

pub struct Terminal<> {
    input: io::Stdin,
    output: io::Stdout,
    mode: TerminalMode,
    _db_connection: sqlite::Connection,
    cmd: Option<Vec<String>>,
    exit: bool,
}

impl Terminal {
    pub fn new(input: io::Stdin, output: io::Stdout , db_path: &str) -> Result<Terminal, Error> {
        Ok(Terminal {
            input,
            output,
            mode: TerminalMode::UserMode,
            _db_connection: sqlite::open(db_path).expect("Error finding db"),
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
            TerminalMode::_DevMode => { self.mode = TerminalMode::UserMode; },
            TerminalMode::UserMode => { self.mode = TerminalMode::_DevMode; },
        }
        self
    }

    fn read_command(mut self) -> Self {
        match self.mode {
            TerminalMode::_DevMode => { write!(self.output, "<?> ").expect("Error outputting Text"); },
            TerminalMode::UserMode => { write!(self.output, ">>> ").expect("Error outputting text"); },
        }
        self.output.flush().expect("Flush failed");
        let mut cmd_text = String::new();
        if let Ok(_) =  self.input.read_line(&mut cmd_text) {
            cmd_text = String::from(cmd_text.trim());
            cmd_text.push(' ');
            match Terminal::str_to_vec(cmd_text) {
                Ok(v) => self.cmd = Some(v),
                Err(e) => {
                    match e {
                        ParsingError::QuotesInWords => writeln!(self.output, "No quotes allowed within a word").unwrap(),
                        ParsingError::UnclosedQuotes => writeln!(self.output, "Unclosed quotes!").unwrap(),
                        ParsingError::NoSpaceAfterQuote => writeln!(self.output, "After closing a quote, leave a space").unwrap(),

                    };
                    self.cmd = None },
            }
        } else {
            self.cmd = None;
        }
        self
    }

    fn str_to_vec(s: String) -> Result<Vec<String>, ParsingError> {
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
        self
    }

    pub fn destroy(self) {}

}