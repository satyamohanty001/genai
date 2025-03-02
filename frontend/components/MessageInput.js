class MessageInput {
    constructor(inputSelector, buttonSelector) {
        this.input = document.querySelector(inputSelector);
        this.button = document.querySelector(buttonSelector);
    }

    getValue() {
        return this.input.value;
    }

    clear() {
        this.input.value = '';
        this.input.style.height = 'auto';
    }

    setDisabled(disabled) {
        this.input.disabled = disabled;
        this.button.disabled = disabled;
    }

    focus() {
        this.input.focus();
    }
}

export default MessageInput;