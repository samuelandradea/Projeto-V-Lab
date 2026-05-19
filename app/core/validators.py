def validate_cpf(cpf: str) -> bool:
    if len(cpf) != 11 or not cpf.isdigit():
        return False

    if cpf == cpf[0] * 11:
        return False

    # First check digit
    total = sum(int(cpf[i]) * (10 - i) for i in range(9))
    remainder = total % 11
    first_digit = 0 if remainder < 2 else 11 - remainder
    if int(cpf[9]) != first_digit:
        return False

    # Second check digit
    total = sum(int(cpf[i]) * (11 - i) for i in range(10))
    remainder = total % 11
    second_digit = 0 if remainder < 2 else 11 - remainder
    return int(cpf[10]) == second_digit
