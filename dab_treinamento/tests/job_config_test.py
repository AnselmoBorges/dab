from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
JOB_FILE = ROOT / "resources" / "jobs" / "dab_treinamento.job.yml"


def _load_job():
    data = yaml.safe_load(JOB_FILE.read_text())
    job = data["resources"]["jobs"]["dab_treinamento_job"]
    return job


def test_job_has_description_and_tags():
    job = _load_job()
    print("Validando descrição do job...")
    assert job.get("description"), "Job description must be set"
    print("Descrição OK!")
    tags = job.get("tags", {})
    print(f"Validando tags obrigatórias: {list(tags.keys())}")
    for tag_key in ("treinamento", "ambiente", "area"):
        assert tag_key in tags, f"Tag '{tag_key}' está ausente"
    print("Tags obrigatórias OK!")


def test_job_has_schedule_and_timeout():
    job = _load_job()
    print("Validando agendamento e timeout...")
    schedule = job.get("schedule")
    assert schedule, "Job schedule deve estar configurado"
    print(f"Agendamento encontrado: {schedule['quartz_cron_expression']} ({schedule['timezone_id']})")
    assert schedule["quartz_cron_expression"].lower() == "0 0 8 ? * tue *"
    assert schedule["timezone_id"] == "America/Sao_Paulo"
    assert job.get("timeout_seconds") == 900
    print("Agendamento e timeout OK!")


def test_job_parameters_exposed():
    job = _load_job()
    params = {p["name"]: p["default"] for p in job.get("parameters", [])}
    print(f"Validando parâmetros expostos: {list(params.keys())}")
    for expected in ("catalog_name", "user_id", "user_name"):
        assert expected in params, f"Parâmetro '{expected}' não configurado"
    print("Parâmetros obrigatórios OK!")


def test_job_uses_variable_for_performance_target():
    job = _load_job()
    print("Validando uso da variável performance_target...")
    assert job.get("performance_target") == "${var.performance_target}"
    print("performance_target OK!")
