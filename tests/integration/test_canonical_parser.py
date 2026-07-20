from distributed_discovery.canonical.reproduce import _parse_metrics


def test_parse_upstream_canonical_block() -> None:
    output = """Canonical independent values
  consensus              0.383468709731
  symmetric market       0.599099252439
  private clue-following 0.832227840000
  planner portfolio      0.859421246199
  E distinct (market)    2.673494083278
  E distinct (private)   6.156849828175
  crossover c*           0.788461656521 at G=0.433893464268
"""
    metrics = _parse_metrics(output)
    assert metrics["market"] == 0.599099252439
    assert metrics["crossover"] == 0.788461656521
