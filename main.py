from vk import Poll
from config import login, password

def main():
    rate = 3600
    output_dir = "test_dir"
    poll = Poll(login, password, output_dir, rate)
    poll.mainloop()

main()
