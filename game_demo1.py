import csv
import random
from dataclasses import dataclass

@dataclass
class Quote:
    text: str
    author: str
    bio: str
    birthdate: str
    birthplace: str
    description: str

    def __repr__(self) -> str:
        return f"Quote('{self.text}', '{self.author}')"

MAX_GUESSES = 4
NUM_HINTS = 3

def load_quotes_from_csv(filename: str) -> list[Quote]:
    """Load quotes from a CSV file."""
    quotes = []
    with open(filename, 'r', encoding='latin1', newline='') as file:
        reader = csv.reader(file, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        next(reader)  # Skip header row
        for row in reader:
            quote = Quote(
                text=row[0],
                author=row[1],
                bio=row[2],
                birthdate=row[3],
                birthplace=row[4],
                description=row[5]
            )
            quotes.append(quote)
    return quotes

def get_random_quote(quotes: list[Quote]) -> Quote:
    """Get a random quote from the list."""
    return random.choice(quotes)

def play_game(quotes: list[Quote]) -> None:
    """Play the guessing game."""
    quote = get_random_quote(quotes)
    guesses_remaining = MAX_GUESSES
    hints_given = 0

    print("Welcome to the guessing game!")
    print(f"Here's your quote: {quote.text}")
    print("Who said that? (You have {} guesses remaining)".format(MAX_GUESSES))

    while guesses_remaining > 0:
        guess = input().strip()
        if guess.lower() == quote.author.lower():
            print("Congratulations! You won!")
            break
        else:
            guesses_remaining -= 1
            print(f"Incorrect. You have {guesses_remaining} guesses remaining.")

            if hints_given == 0:
                print(f"Hint: The author was born in {quote.birthplace} {quote.birthdate}.")
            elif hints_given == 1:
                print(f"Hint: The author's initials are {quote.author.split()[0][0]}.{quote.author.split()[-1][0]}.")
            elif hints_given == 2:
                print(f"Hint: The author is known for {quote.description.split('.')[0]}.")
            hints_given += 1

    if guesses_remaining == 0:
        print(f"Game over! The correct answer was {quote.author}.")

    play_again = input("Would you like to play again? (y/n): ")
    if play_again.lower() == 'y':
        play_game(quotes)
    else:
        print("Thanks for playing!")

if __name__ == "__main__":
    quotes = load_quotes_from_csv('quotes.csv')
    play_game(quotes)