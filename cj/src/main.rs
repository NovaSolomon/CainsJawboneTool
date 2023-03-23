use std::io;
use std::io::Write;

fn main() {
    println!("This will be a test for my game terminal:");

    print!(">>> ");

    io::stdout().flush().expect("flush failed");

    let mut guess = String::new();

    io::stdin()
        .read_line(&mut guess)
        .expect("Failed to read line");
    if guess.trim() == "bruh" { println!("      It worked!"); }
} 
