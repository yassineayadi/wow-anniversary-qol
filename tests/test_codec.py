from wa_project.codec import decode, encode


def test_round_trip_keeps_wa2_shape(sample_import: str) -> None:
    data = decode(sample_import)
    encoded = encode(data)
    decoded_again = decode(encoded)
    assert encoded.startswith("!WA:2!")
    assert decoded_again == data
