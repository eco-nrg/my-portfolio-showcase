from py_scripts.state import get_state


def main():
    state = get_state()
    json_data = state.json()
    print(json_data)


if __name__ == '__main__':
    main()
