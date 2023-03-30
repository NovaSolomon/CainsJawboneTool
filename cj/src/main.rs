use cj::Terminal;

fn main() {
    let terminal = Terminal::new(std::io::stdin(), std::io::stdout(), "../db/evidence_board.db").unwrap();
    terminal.serve();
} 
