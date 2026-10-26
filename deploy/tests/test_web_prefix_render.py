""" /kubedoor/ 与原来的地址并存,前缀片段来自独立文件。"""

from test_auth_render import block, render_master


def test_prefix_reuses_existing_locations(tmp_path):
    docs, _ = render_master(tmp_path)
    conf = docs[("ConfigMap", "nginx-config")]["data"]["nginx.conf"]
    assert "map $request_uri $kd_prefix" in conf
    assert "location = /kubedoor" in conf
    assert "rewrite ^/kubedoor/(.*)$ /$1 last;" in block(conf, "location ^~ /kubedoor/")
    master = block(conf, "location ~ ^/(api|ws)(/|$)")
    assert "proxy_set_header X-Forwarded-Prefix $kd_prefix;" in master
    grafana = block(conf, "location ^~ /kubedoor/grafana/")
    assert "proxy_pass http://kubedoor-dash.ai-render-test:3000/grafana/;" in grafana
    assert "sub_filter '/grafana/' '/kubedoor/grafana/';" in grafana
    assert conf.count("location /grafana/") == 1


def test_prefix_grafana_block_follows_grafana_switch(tmp_path):
    docs, _ = render_master(tmp_path / "off", ("ENABLE_GRAFANA=false",))
    conf = docs[("ConfigMap", "nginx-config")]["data"]["nginx.conf"]
    assert "location ^~ /kubedoor/" in conf
    assert "location ^~ /kubedoor/grafana/" not in conf
    assert "kubedoor-dash" not in conf
