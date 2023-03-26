use cj::Terminal;

fn main() {
    let terminal = Terminal::new(std::io::stdin(), std::io::stdout(), "../db/evidence_board.db").unwrap();
    terminal.serve();
    let v = vec![String::from("word 1"), String::from("word 2")];
    match v[0].as_str() {
        "word 1" => println!("success!"),
        _ => println!("fuck"),
    }
} 
