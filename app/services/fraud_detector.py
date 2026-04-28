from app.database.redis_client import get_redis

redis = get_redis()

def check_velocity(user_id: str) -> bool:
    """
    Aynı kullanıcıdan son 1 dakikada 5'ten fazla işlem var mı?
    """
    key = f"tx_count:{user_id}"

    count = redis.get(key)
    count = int(count) if count else 0

    count += 1

    # 60 saniye boyunca bu sayacı tut
    redis.setex(key, 60, count)

    is_fraud = count > 5
    print(f"🔍 [Velocity] user={user_id} | count={count} | fraud={is_fraud}")

    return is_fraud


def check_amount(user_id: str, amount: float) -> bool:
    """
    İşlem tutarı, kullanıcının son işlemlerinin ortalamasının 3 katından fazla mı?
    Basit MVP yaklaşımı: Redis'te son 100 tutarı tutuyoruz.
    """
    key = f"tx_amounts:{user_id}"

    amounts_str = redis.get(key)

    # Kullanıcının önceki işlemi yoksa fraud değil, sadece tutarı kaydet
    if not amounts_str:
        redis.setex(key, 86400, str(amount))
        print(f"🔍 [Amount] user={user_id} | ilk işlem | fraud=False")
        return False

    # Redis'teki string'i float listesine çevir
    amounts = [float(x) for x in amounts_str.split(",") if x]

    avg = sum(amounts) / len(amounts) if amounts else 0

    # Mevcut işlem, önceki ortalamanın 3 katından büyük mü?
    is_fraud = amount > (avg * 3) if avg > 0 else False

    # Yeni amount'u listeye ekle
    amounts.append(float(amount))

    # Son 100 işlemi tut
    if len(amounts) > 100:
        amounts = amounts[-100:]

    # Listeyi tekrar string'e çevirip Redis'e yaz
    redis.setex(key, 86400, ",".join(str(x) for x in amounts))

    print(f"🔍 [Amount] user={user_id} | avg={avg:.2f} | amount={amount} | fraud={is_fraud}")

    return is_fraud


def detect_fraud(user_id: str, amount: float) -> bool:
    """
    MVP için:
    Velocity veya Amount kurallarından biri tetiklenirse fraud sayıyoruz.
    """
    velocity_result = check_velocity(user_id)
    amount_result = check_amount(user_id, amount)

    result = velocity_result or amount_result

    print(
        f"🚨 [Detect] user={user_id} | "
        f"velocity={velocity_result} | amount={amount_result} | result={result}"
    )

    return result
