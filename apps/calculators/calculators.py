"""Pure Python financial calculation functions — no Django ORM."""


def _round2(value):
    return round(float(value), 2)


def calculate_loan_annuity(principal, annual_rate_pct, term_months):
    """Standard annuity loan. Returns monthly_payment, total_payment, total_interest, schedule."""
    principal = float(principal)
    annual_rate = float(annual_rate_pct)
    n = int(term_months)

    if annual_rate == 0:
        monthly_payment = principal / n
        schedule = []
        balance = principal
        for i in range(1, n + 1):
            balance -= monthly_payment
            schedule.append({
                'month': i,
                'payment': _round2(monthly_payment),
                'principal': _round2(monthly_payment),
                'interest': 0.0,
                'balance': _round2(max(balance, 0)),
            })
        return {
            'monthly_payment': _round2(monthly_payment),
            'total_payment': _round2(monthly_payment * n),
            'total_interest': 0.0,
            'schedule': schedule,
        }

    r = annual_rate / 100 / 12
    monthly_payment = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    total_payment = monthly_payment * n
    total_interest = total_payment - principal

    schedule = []
    balance = principal
    for i in range(1, n + 1):
        interest = balance * r
        principal_part = monthly_payment - interest
        balance -= principal_part
        schedule.append({
            'month': i,
            'payment': _round2(monthly_payment),
            'principal': _round2(principal_part),
            'interest': _round2(interest),
            'balance': _round2(max(balance, 0)),
        })

    return {
        'monthly_payment': _round2(monthly_payment),
        'total_payment': _round2(total_payment),
        'total_interest': _round2(total_interest),
        'schedule': schedule,
    }


def calculate_mortgage(principal, annual_rate_pct, term_months, down_payment=0, property_value=None):
    """Mortgage with down payment and LTV."""
    loan_amount = float(principal) - float(down_payment)
    result = calculate_loan_annuity(loan_amount, annual_rate_pct, term_months)
    result['loan_amount'] = _round2(loan_amount)
    result['down_payment'] = _round2(float(down_payment))
    if property_value:
        result['ltv_pct'] = _round2((loan_amount / float(property_value)) * 100)
    result['total_cost'] = _round2(result['total_payment'] + float(down_payment))
    return result


def calculate_investment_return(initial, monthly_contribution, annual_rate_pct, years):
    """Compound interest with monthly contributions."""
    initial = float(initial)
    monthly = float(monthly_contribution)
    r = float(annual_rate_pct) / 100 / 12
    months = int(years) * 12

    balance = initial
    total_contributed = initial
    yearly = []

    for month in range(1, months + 1):
        balance = balance * (1 + r) + monthly
        total_contributed += monthly
        if month % 12 == 0:
            yearly.append({
                'year': month // 12,
                'balance': _round2(balance),
                'contributed': _round2(total_contributed),
                'gain': _round2(balance - total_contributed),
            })

    return {
        'final_value': _round2(balance),
        'total_contributed': _round2(total_contributed),
        'total_gain': _round2(balance - total_contributed),
        'yearly_breakdown': yearly,
    }


def calculate_savings_goal(target_amount, current_savings, annual_rate_pct, monthly_contribution):
    """How many months to reach a savings target."""
    target = float(target_amount)
    balance = float(current_savings)
    monthly = float(monthly_contribution)
    r = float(annual_rate_pct) / 100 / 12

    if balance >= target:
        return {'months_to_goal': 0, 'years': 0, 'total_contributions': 0,
                'interest_earned': 0, 'achievable': True}

    months = 0
    max_months = 600
    while balance < target and months < max_months:
        balance = balance * (1 + r) + monthly
        months += 1

    achievable = balance >= target
    return {
        'months_to_goal': months,
        'years': round(months / 12, 1),
        'total_contributions': _round2(float(current_savings) + monthly * months),
        'interest_earned': _round2(balance - float(current_savings) - monthly * months),
        'achievable': achievable,
    }


def compare_loan_offers(principal, term_months, offers):
    """Compare multiple bank offers sorted by monthly_payment."""
    results = []
    for offer in offers:
        calc = calculate_loan_annuity(principal, offer['rate'], term_months)
        results.append({
            'name': offer['name'],
            'rate': offer['rate'],
            'monthly_payment': calc['monthly_payment'],
            'total_payment': calc['total_payment'],
            'total_interest': calc['total_interest'],
        })
    return sorted(results, key=lambda x: x['monthly_payment'])
