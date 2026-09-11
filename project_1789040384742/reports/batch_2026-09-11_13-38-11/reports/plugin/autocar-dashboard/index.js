'use strict';
/* AutoCar Dashboard — Allure tab plugin
 * Visual style ported from the old `perf-monitor` widget plugin
 * (light cards, compact SVGs). Keeps the Tab/AppLayout structure that
 * was already accepted by the user — only the rendering style changed.
 *
 * Data sources (written by autocar test runs, copied to widgets/ by
 *   autocar.cli allure post-generate):
 *   - widgets/perf-monitor.json    (drivers/u2/perf.py::_perf_write_widget_json)
 *   - widgets/anomaly-monitor.json (_internal/anomaly.py::write_widget_json)
 */
allure.api.addTranslation('en', { tab: { autocarDashboard: { name: 'Dashboard' } } });
allure.api.addTranslation('zh', { tab: { autocarDashboard: { name: '仪表盘' } } });
allure.api.addTranslation('ru', { tab: { autocarDashboard: { name: 'Dashboard' } } });

(function () {
    function esc(s) {
        return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }

    // High-fidelity line chart with grid, smooth curve, gradient fill and
    // hover crosshair+tooltip. viewBox 800x180. Padding: L40 R10 T10 B30.
    // Data points serialized via data-* attrs for hover-time lookup.
    function compactChart(points, color, opts) {
        var pts = points || [];
        opts = opts || {};
        var duration = Number(opts.duration) || 0;
        var startTs = Number(opts.startTs) || 0;  // epoch seconds; if >0 use HH:mm:ss
        var unit = opts.unit || '';
        var W = 800, H = 120, PL = 36, PR = 8, PT = 8, PB = 22;
        var IW = W - PL - PR, IH = H - PT - PB;
        if (pts.length < 2) return '<div class="pm-chart"><svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" preserveAspectRatio="none"></svg></div>';

        var mn = pts[0], mx = pts[0];
        for (var p = 0; p < pts.length; p++) { if (pts[p] < mn) mn = pts[p]; if (pts[p] > mx) mx = pts[p]; }
        // Pad Y range 10% so the line isn't glued to top/bottom.
        var range = mx - mn || 1;
        var yMin = Math.max(0, mn - range * 0.1);
        var yMax = mx + range * 0.1;
        if (yMax === yMin) yMax = yMin + 1;

        function sx(i) { return PL + (i / (pts.length - 1)) * IW; }
        function sy(v) { return PT + IH - ((v - yMin) / (yMax - yMin)) * IH; }

        // Smooth path via cardinal-spline-ish bezier (tension 0.5).
        var path = 'M' + sx(0).toFixed(1) + ',' + sy(pts[0]).toFixed(1);
        for (var i = 0; i < pts.length - 1; i++) {
            var p0 = i > 0 ? pts[i - 1] : pts[i];
            var p1 = pts[i], p2 = pts[i + 1];
            var p3 = i < pts.length - 2 ? pts[i + 2] : p2;
            var cp1x = sx(i) + (sx(i + 1) - sx(i - 1 < 0 ? 0 : i - 1)) / 6;
            var cp1y = sy(p1) + (sy(p2) - sy(p0)) / 6;
            var cp2x = sx(i + 1) - (sx(i + 2 > pts.length - 1 ? pts.length - 1 : i + 2) - sx(i)) / 6;
            var cp2y = sy(p2) - (sy(p3) - sy(p1)) / 6;
            path += ' C' + cp1x.toFixed(1) + ',' + cp1y.toFixed(1)
                + ' ' + cp2x.toFixed(1) + ',' + cp2y.toFixed(1)
                + ' ' + sx(i + 1).toFixed(1) + ',' + sy(p2).toFixed(1);
        }
        var area = path + ' L' + sx(pts.length - 1).toFixed(1) + ',' + (PT + IH)
            + ' L' + sx(0).toFixed(1) + ',' + (PT + IH) + ' Z';

        // Y-axis ticks (4 segments → 5 labels).
        function fmtY(v) {
            if (Math.abs(v) >= 100) return v.toFixed(0);
            if (Math.abs(v) >= 10) return v.toFixed(1);
            return v.toFixed(2);
        }
        var yTicks = '';
        for (var t = 0; t <= 4; t++) {
            var v = yMin + (yMax - yMin) * (4 - t) / 4;
            var y = PT + (IH * t / 4);
            yTicks += '<line x1="' + PL + '" y1="' + y + '" x2="' + (W - PR) + '" y2="' + y
                + '" stroke="#eef2f7" stroke-width="1"/>'
                + '<text x="' + (PL - 6) + '" y="' + (y + 3) + '" text-anchor="end" '
                + 'font-size="10" fill="#64748b">' + fmtY(v) + '</text>';
        }

        // X-axis time ticks (5 segments → 6 ticks).
        function pad2(n) { return n < 10 ? '0' + n : '' + n; }
        function fmtClock(sec) {
            var d = new Date(sec * 1000);
            return pad2(d.getHours()) + ':' + pad2(d.getMinutes()) + ':' + pad2(d.getSeconds());
        }
        function fmtRel(sec) {
            if (sec < 60) return Math.round(sec) + 's';
            var m = Math.floor(sec / 60), s = Math.round(sec % 60);
            return m + 'm' + (s ? s + 's' : '');
        }
        var useClock = startTs > 0;
        var xTicks = '';
        var TICK_N = 5;
        for (var t = 0; t <= TICK_N; t++) {
            var tx = PL + (IW * t / TICK_N);
            var lbl = '';
            if (duration > 0) {
                var sec = duration * t / TICK_N;
                lbl = useClock ? fmtClock(startTs + sec) : fmtRel(sec);
            }
            xTicks += '<line x1="' + tx + '" y1="' + (PT + IH) + '" x2="' + tx + '" y2="' + (PT + IH + 4)
                + '" stroke="#cbd5e1" stroke-width="1"/>'
                + '<text x="' + tx + '" y="' + (PT + IH + 16) + '" text-anchor="middle" '
                + 'font-size="10" fill="#64748b">' + lbl + '</text>';
        }

        var gradId = 'pmg_' + Math.random().toString(36).slice(2, 8);
        var dataAttr = ' data-points="' + pts.join(',') + '"'
            + ' data-color="' + color + '"'
            + ' data-duration="' + duration + '"'
            + ' data-start-ts="' + startTs + '"'
            + ' data-unit="' + esc(unit) + '"'
            + ' data-ymin="' + yMin.toFixed(4) + '"'
            + ' data-ymax="' + yMax.toFixed(4) + '"';
        return '<div class="pm-chart"' + dataAttr + '>'
            + '<svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" preserveAspectRatio="none">'
            + '<defs><linearGradient id="' + gradId + '" x1="0" x2="0" y1="0" y2="1">'
            + '<stop offset="0%" stop-color="' + color + '" stop-opacity="0.35"/>'
            + '<stop offset="100%" stop-color="' + color + '" stop-opacity="0.02"/>'
            + '</linearGradient></defs>'
            + yTicks
            + '<path d="' + area + '" fill="url(#' + gradId + ')"/>'
            + '<path d="' + path + '" fill="none" stroke="' + color + '" stroke-width="1.8" stroke-linejoin="round"/>'
            + '<line x1="' + PL + '" y1="' + (PT + IH) + '" x2="' + (W - PR) + '" y2="' + (PT + IH) + '" stroke="#cbd5e1"/>'
            + xTicks
            + '<g class="pm-hover" style="display:none">'
            + '<line class="pm-hv-line" x1="0" y1="' + PT + '" x2="0" y2="' + (PT + IH) + '" stroke="#94a3b8" stroke-dasharray="3,3"/>'
            + '<circle class="pm-hv-dot" cx="0" cy="0" r="4" fill="#fff" stroke="' + color + '" stroke-width="2"/>'
            + '</g>'
            + '<rect class="pm-hv-zone" x="' + PL + '" y="' + PT + '" width="' + IW + '" height="' + IH + '" fill="transparent"/>'
            + '</svg>'
            + '<div class="pm-tip" style="display:none"></div>'
            + '</div>';
    }

    var TYPE_COLOR = { cpu: '#3b82f6', mem: '#8b5cf6', fps: '#10b981', io: '#f59e0b' };
    var TYPE_UNIT = { cpu: '%', mem: '%', fps: '', io: 'KB/s' };

    function renderPerf(d) {
        if (!d || !d.items || !d.items.length) {
            return '<div class="pm-empty">No performance data available</div>';
        }
        var it = d.items[0];
        var h = '';

        h += '<div class="pm-hdr"><h3>' + esc(it.title || 'Performance Monitor') + '</h3>';
        if (it.pkg) h += '<span class="pm-badge">' + esc(it.pkg) + '</span>';
        h += '</div>';

        h += '<div class="pm-meta">'
            + 'Duration: <b>' + esc(it.duration || '-') + '</b>'
            + ' &middot; Samples: <b>' + (it.samples || 0) + '</b>'
            + ' &middot; Sessions: <b>' + (it.sessions || 0) + '</b>'
            + '</div>';

        var kpis = it.kpis || [];
        if (kpis.length) {
            h += '<div class="pm-krow">';
            for (var k = 0; k < kpis.length; k++) {
                h += '<div class="pm-kpi"><div class="pm-kv">' + esc(kpis[k].value) + '</div>'
                    + '<div class="pm-kl">' + esc(kpis[k].label) + '</div></div>';
            }
            h += '</div>';
        }

        // Parse "120.0s" / "5m30s" / "330" → seconds for X-axis tick labels.
        function parseDur(s) {
            if (s == null) return 0;
            if (typeof s === 'number') return s;
            var str = String(s);
            var sec = 0, m;
            if ((m = str.match(/(\d+(?:\.\d+)?)\s*m/))) sec += parseFloat(m[1]) * 60;
            if ((m = str.match(/(\d+(?:\.\d+)?)\s*s/))) sec += parseFloat(m[1]);
            if (sec === 0) sec = parseFloat(str) || 0;
            return sec;
        }
        var durSec = parseDur(it.duration);
        var startTs = Number(it.start_ts) || 0;

        var charts = it.charts || [];
        if (charts.length) {
            h += '<div class="pm-pair">';
            for (var c = 0; c < charts.length; c++) {
                var ch = charts[c];
                var clr = TYPE_COLOR[ch.type] || '#9ca3af';
                h += '<div class="pm-cb">'
                    + '<div class="pm-ct">' + esc(ch.name) + '</div>'
                    + compactChart(ch.points, clr, { duration: durSec, startTs: startTs, unit: TYPE_UNIT[ch.type] || '' })
                    + '<div class="pm-st">'
                    + '<span>Min: ' + (ch.min != null ? ch.min.toFixed(1) : '-') + '</span>'
                    + '<span>Avg: ' + (ch.avg != null ? ch.avg.toFixed(1) : '-') + '</span>'
                    + '<span>Max: ' + (ch.max != null ? ch.max.toFixed(1) : '-') + '</span>'
                    + '</div></div>';
            }
            h += '</div>';
        }

        function multiLineChart(lines, opts) {
            // Render N processes as overlaid lines on a single chart.
            // Each line: { name, points: number[] }. Legend below.
            opts = opts || {};
            var W = 800, H = 160, PL = 36, PR = 8, PT = 8, PB = 22;
            var IW = W - PL - PR, IH = H - PT - PB;
            if (!lines || !lines.length) return '';
            // Parse points to arrays of numbers
            var series = [];
            for (var i = 0; i < lines.length; i++) {
                var p = lines[i].points;
                if (typeof p === 'string') {
                    p = p.split(/[\s,]+/).filter(Boolean).map(parseFloat);
                }
                if (!p || !p.length) continue;
                series.push({ name: lines[i].name, pts: p });
            }
            if (!series.length) return '';
            var maxLen = 0, mn = Infinity, mx = -Infinity;
            for (var s = 0; s < series.length; s++) {
                if (series[s].pts.length > maxLen) maxLen = series[s].pts.length;
                for (var k = 0; k < series[s].pts.length; k++) {
                    var v = series[s].pts[k];
                    if (v < mn) mn = v;
                    if (v > mx) mx = v;
                }
            }
            var range = mx - mn || 1;
            var yMin = Math.max(0, mn - range * 0.1);
            var yMax = mx + range * 0.1;
            if (yMax === yMin) yMax = yMin + 1;
            function sx(i, n) { return PL + (i / (n - 1)) * IW; }
            function sy(v) { return PT + IH - ((v - yMin) / (yMax - yMin)) * IH; }
            var PALETTE = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
                           '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'];
            // Y grid + ticks (4 lines)
            var grid = '';
            for (var t = 0; t <= 4; t++) {
                var y = PT + (IH * t / 4);
                var yv = yMin + (yMax - yMin) * (4 - t) / 4;
                grid += '<line x1="' + PL + '" y1="' + y + '" x2="' + (PL + IW) + '" y2="' + y
                    + '" stroke="#eef2f7" stroke-width="1"/>'
                    + '<text x="' + (PL - 4) + '" y="' + (y + 3) + '" text-anchor="end" '
                    + 'font-size="9" fill="#94a3b8">' + yv.toFixed(0) + (opts.unit || '') + '</text>';
            }
            // X ticks
            var duration = opts.duration || 0, startTs = opts.startTs || 0;
            var xTicks = '';
            for (var xi = 0; xi <= 5; xi++) {
                var tx = PL + (IW * xi / 5);
                var lbl = '';
                if (duration > 0) {
                    var sec = duration * xi / 5;
                    if (startTs > 0) {
                        var d = new Date((startTs + sec) * 1000);
                        lbl = ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2) + ':' + ('0' + d.getSeconds()).slice(-2);
                    } else { lbl = sec.toFixed(0) + 's'; }
                }
                xTicks += '<line x1="' + tx + '" y1="' + (PT + IH) + '" x2="' + tx + '" y2="' + (PT + IH + 4) + '" stroke="#cbd5e1"/>'
                    + '<text x="' + tx + '" y="' + (PT + IH + 14) + '" text-anchor="middle" font-size="9" fill="#64748b">' + lbl + '</text>';
            }
            // Polylines
            var paths = '';
            for (var si = 0; si < series.length; si++) {
                var pts = series[si].pts;
                var d = '';
                for (var pi = 0; pi < pts.length; pi++) {
                    d += (pi === 0 ? 'M' : 'L') + sx(pi, pts.length).toFixed(1) + ',' + sy(pts[pi]).toFixed(1) + ' ';
                }
                var color = PALETTE[si % PALETTE.length];
                paths += '<path class="pm-ml-line" data-idx="' + si + '" d="' + d + '" fill="none" stroke="' + color + '" stroke-width="1.4" opacity="0.85"/>';
            }
            // Hover overlay (full plot area) + crosshair line + per-series dots + tooltip
            var hover = '<g class="pm-ml-hover" style="display:none">'
                + '<line class="pm-ml-vline" x1="0" y1="' + PT + '" x2="0" y2="' + (PT + IH) + '" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3,3"/>';
            for (var di = 0; di < series.length; di++) {
                hover += '<circle class="pm-ml-dot" data-idx="' + di + '" r="3" fill="' + PALETTE[di % PALETTE.length] + '" stroke="#fff" stroke-width="1.5"/>';
            }
            hover += '</g>'
                + '<rect class="pm-ml-zone" x="' + PL + '" y="' + PT + '" width="' + IW + '" height="' + IH + '" fill="transparent"/>';
            // Serialize series + meta to data-attrs for the wireup script.
            var seriesJson = JSON.stringify(series.map(function (s) {
                return { name: s.name, pts: s.pts };
            }));
            var svg = '<div class="pm-chart pm-mlchart"'
                + ' data-series=\'' + seriesJson.replace(/'/g, '&#39;') + '\''
                + ' data-pl="' + PL + '" data-pr="' + PR + '" data-pt="' + PT + '" data-pb="' + PB + '"'
                + ' data-w="' + W + '" data-h="' + H + '"'
                + ' data-ymin="' + yMin + '" data-ymax="' + yMax + '"'
                + ' data-duration="' + duration + '" data-start-ts="' + startTs + '"'
                + ' data-unit="' + (opts.unit || '') + '">'
                + '<svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" preserveAspectRatio="none">'
                + grid + xTicks + paths + hover + '</svg>'
                + '<div class="pm-tip" style="display:none"></div>'
                + '</div>';
            // Legend (clickable)
            var legend = '<div class="pm-legend">';
            for (var li = 0; li < series.length; li++) {
                var c = PALETTE[li % PALETTE.length];
                var last = series[li].pts[series[li].pts.length - 1];
                legend += '<span class="pm-leg-it pm-leg-clk" data-idx="' + li + '" title="' + esc(series[li].name) + '">'
                    + '<span class="pm-leg-sw" style="background:' + c + '"></span>'
                    + '<span class="pm-leg-nm">' + esc(series[li].name) + '</span>'
                    + '<span class="pm-leg-vv">' + last.toFixed(1) + (opts.unit || '') + '</span>'
                    + '</span>';
            }
            legend += '</div>';
            return svg + legend;
        }
        if ((it.top_cpu && it.top_cpu.length) || (it.top_mem && it.top_mem.length)) {
            h += '<div class="pm-pair">';
            if (it.top_cpu && it.top_cpu.length) {
                h += '<div class="pm-cb">'
                    + '<div class="pm-ct">Top 10 进程 CPU</div>'
                    + multiLineChart(it.top_cpu, { duration: durSec, startTs: startTs, unit: '%' })
                    + '</div>';
            }
            if (it.top_mem && it.top_mem.length) {
                h += '<div class="pm-cb">'
                    + '<div class="pm-ct">Top 10 进程 MEM</div>'
                    + multiLineChart(it.top_mem, { duration: durSec, startTs: startTs, unit: 'MB' })
                    + '</div>';
            }
            h += '</div>';
        }
        return h;
    }

    // Anomaly type → pill color (matches reference design: light bg + bold text).
    var TYPE_PILL = {
        anr:           { bg: '#fee2e2', fg: '#b91c1c' },
        crash:         { bg: '#ffedd5', fg: '#c2410c' },
        tombstone:     { bg: '#fef3c7', fg: '#92400e' },
        freeze:        { bg: '#dbeafe', fg: '#1e40af' },
        glitch:        { bg: '#f3e8ff', fg: '#7e22ce' },
        black:         { bg: '#e5e7eb', fg: '#1f2937' },
        white:         { bg: '#f3f4f6', fg: '#6b7280' },
        half:          { bg: '#cffafe', fg: '#0e7490' },
        capture:       { bg: '#ecfccb', fg: '#4d7c0f' },
        cpu_violation: { bg: '#ccfbf1', fg: '#0f766e' },
        mem_violation: { bg: '#d1fae5', fg: '#047857' },
        mem_leak:      { bg: '#fecaca', fg: '#991b1b' }
    };
    function typePill(type, count) {
        var c = TYPE_PILL[type] || { bg: '#e5e7eb', fg: '#374151' };
        var label = esc(type) + (count != null ? ' <b>' + count + '</b>' : '');
        return '<span class="pm-pill" style="background:' + c.bg + ';color:' + c.fg + '">' + label + '</span>';
    }

    function isUnpackagedPath(value) {
        var s = String(value || '').trim();
        return /^[A-Za-z]:[\\/]/.test(s) || /^file:/i.test(s) || /^\\\\/.test(s);
    }

    function fmtFileSize(n) {
        n = Number(n) || 0;
        if (!n) return '';
        if (n < 1024) return n + ' B';
        if (n < 1048576) return (n / 1024).toFixed(1) + ' KB';
        return (n / 1048576).toFixed(1) + ' MB';
    }

    // Group screenshot column to a colored rectangle (visual category cue).
    var SHOT_COLOR = {
        black: '#1f2937', white: '#f3f4f6', half: '#3b82f6', freeze: '#64748b',
        glitch: '#a855f7', capture: '#84cc16'
    };

    // Anomaly renderer matches the reference image (20260519-132849.jpg):
    // 3 group KPI cards (稳定性/性能/显示) + type pills row + detail table
    // (no separate group breakdown — user explicit "异常不需要分组").
    function renderAnomaly(raw) {
        var d = raw && raw.items && raw.items.length ? raw.items[0] : null;
        if (!d) return '<div class="pm-empty">无异常数据</div>';
        if (!d.total) {
            return '<div class="pm-empty">本次运行未记录任何异常 (run_id=' + esc(d.run_id || '-') + ')</div>';
        }

        var h = '';
        h += '<div class="pm-hdr"><h3>Anomaly Summary</h3>'
            + '<span class="pm-badge pm-badge-red">' + (d.total || 0) + ' 事件</span>'
            + '</div>';

        var recent = d.recent || [];
        var post = raw && raw._post_generate;
        var unpackaged = 0;
        for (var rp = 0; rp < recent.length; rp++) {
            var rr = recent[rp] || {};
            if (isUnpackagedPath(rr.screenshot) || isUnpackagedPath(rr.video)
                    || isUnpackagedPath(rr.log_file)) {
                unpackaged++;
            }
        }
        var postFailures = post && post.failures ? post.failures : [];
        if (unpackaged || postFailures.length) {
            h += '<div style="margin:8px 0;padding:10px 12px;border:1px solid #f59e0b;'
                + 'background:#fffbeb;color:#92400e;border-radius:4px">'
                + (unpackaged
                    ? '检测到 ' + unpackaged + ' 条本机路径，资源尚未打包。请重新执行 allure post-generate。'
                    : '部分报告资源未能打包，请检查 post-generate 输出。')
                + (postFailures.length ? ' 缺失资源: ' + postFailures.length + ' 个。' : '')
                + '</div>';
        }

        h += '<div class="pm-meta">'
            + '运行: <b>' + esc(d.run_id || '-') + '</b>'
            + ' &middot; 时间窗: <b>' + esc(d.duration || '-') + '</b>'
            + ' &middot; 设备数: <b>' + (d.device_count || 0) + '</b>'
            + ' &middot; 程序数: <b>' + (d.package_count || 0) + '</b>'
            + '</div>';

        var grp = d.by_group || {};
        var groupDefs = [];

        var types = d.by_type || [];
        if (types.length) {
            h += '<div class="pm-pills">';
            for (var i = 0; i < types.length; i++) {
                h += typePill(types[i].type, types[i].count);
            }
            h += '</div>';
        }

        if (recent.length) {
            // Filter bar: 异常类型 / 程序名 / 用例名称 + 关键字 + 清除 + 计数
            var uniqType = {}, uniqPkg = {}, uniqTc = {};
            for (var u = 0; u < recent.length; u++) {
                if (recent[u].type) uniqType[recent[u].type] = 1;
                if (recent[u].package) uniqPkg[recent[u].package] = 1;
                var tcKey = String(recent[u].test_case || '').split('::').pop();
                if (tcKey) uniqTc[tcKey] = 1;
            }
            function opts(map, anyLabel) {
                var keys = Object.keys(map).sort();
                var s = '<option value="">' + anyLabel + '</option>';
                for (var k = 0; k < keys.length; k++) {
                    s += '<option value="' + esc(keys[k]) + '">' + esc(keys[k]) + '</option>';
                }
                return s;
            }
            var shown = recent.length;
            h += '<div class="pm-flt">'
                + '<select class="pm-flt-type">' + opts(uniqType, '全部类型') + '</select>'
                + '<select class="pm-flt-pkg">' + opts(uniqPkg, '全部程序名') + '</select>'
                + '<select class="pm-flt-tc">' + opts(uniqTc, '全部用例') + '</select>'
                + '<input class="pm-flt-kw" type="text" placeholder="关键字搜索...">'
                + '<button class="pm-flt-clr" type="button">清除</button>'
                + '<span class="pm-flt-cnt"><span class="pm-flt-shown">' + shown + '</span> / ' + recent.length + '</span>'
                + '</div>';

            h += '<table class="pm-tbl pm-tbl-anom"><thead><tr>'
                + '<th>异常类型</th><th>程序名</th><th>用例名称</th><th>发生时间</th>'
                + '<th>LOG文件</th><th>截图</th><th>视频</th></tr></thead><tbody>';
            for (var j = 0; j < recent.length; j++) {
                var r = recent[j];
                var tc = String(r.test_case || '');
                var tcShort = tc.split('::').pop();
                var shotColor = SHOT_COLOR[r.type] || '#cbd5e1';
                var shotCell;
                if (r.screenshot && !isUnpackagedPath(r.screenshot)) {
                    // 缩略图 (相对 URL 由 post-generate 改写) + 点击放大
                    shotCell = '<img class="pm-shot-img pm-img-open" '
                        + 'src="' + esc(r.screenshot) + '" '
                        + 'data-src="' + esc(r.screenshot) + '" '
                        + 'title="' + esc(r.screenshot) + '" '
                        + 'style="width:48px;height:32px;object-fit:cover;border-radius:3px;cursor:pointer;border:1px solid #d1d5db"/>';
                } else if (isUnpackagedPath(r.screenshot)) {
                    shotCell = '<span title="' + esc(r.screenshot) + '" style="color:#b45309">未打包</span>';
                } else {
                    shotCell = '<span class="pm-shot" style="background:' + shotColor + ';opacity:.35" title="无截图"></span>';
                }
                // log cell: post-generate 可关联一个或多个 Monitor logcat，按 Range 分段查看。
                var logCell;
                var logFiles = r.log_files && r.log_files.length ? r.log_files : [];
                if (!logFiles.length && r.log_file) {
                    logFiles = [{ path: r.log_file, name: r.log_file_name, size: r.log_size }];
                }
                if (logFiles.length) {
                    var logLinks = [];
                    var unpackagedLog = false;
                    for (var lf = 0; lf < logFiles.length; lf++) {
                        var logInfo = logFiles[lf] || {};
                        var logPath = logInfo.path || logInfo.source || '';
                        var logName = logInfo.name || String(logPath).split('/').pop();
                        if (!logPath) continue;
                        if (isUnpackagedPath(logPath)) {
                            unpackagedLog = true;
                            continue;
                        }
                        logLinks.push('<a href="#" class="pm-log-open" data-src="' + esc(logPath) + '">'
                            + esc(logName) + '</a>'
                            + (logInfo.size ? ' <small>(' + esc(fmtFileSize(logInfo.size)) + ')</small>' : ''));
                    }
                    logCell = logLinks.length ? logLinks.join('<br/>')
                        : (unpackagedLog ? '<span style="color:#b45309">未打包</span>' : '-');
                } else if (isUnpackagedPath(r.log_file)) {
                    logCell = '<span title="' + esc(r.log_file) + '" style="color:#b45309">未打包</span>';
                } else if (r.log_file_name) {
                    logCell = '<span style="color:#6b7280">'
                        + esc(r.log_file_name)
                        + (r.log_size ? ' <small>(' + esc(fmtFileSize(r.log_size)) + ')</small>' : '')
                        + '</span>';
                } else {
                    logCell = '-';
                }
                var kw = ((r.type || '') + ' ' + (r.package || '') + ' ' + tc + ' '
                    + (r.message || '') + ' ' + (r.source || '')).toLowerCase();
                h += '<tr data-type="' + esc(r.type || '') + '"'
                    + ' data-pkg="' + esc(r.package || '') + '"'
                    + ' data-tc="' + esc(tcShort) + '"'
                    + ' data-kw="' + esc(kw) + '">'
                    + '<td>' + typePill(r.type) + '</td>'
                    + '<td>' + esc(r.package || '-') + '</td>'
                    + '<td title="' + esc(tc) + '">' + esc(tcShort) + '</td>'
                    + '<td>' + esc(r.time) + '</td>'
                    + '<td>' + logCell + '</td>'
                    + '<td>' + shotCell + '</td>'
                    + '<td>' + (r.video && !isUnpackagedPath(r.video)
                        ? '<a href="#" class="pm-vid-open" data-src="' + esc(r.video) + '" title="' + esc(r.video) + '">'
                          + esc((String(r.video).split('/').pop())) + '</a>'
                        : (isUnpackagedPath(r.video) ? '<span style="color:#b45309">未打包</span>' : '-')) + '</td>'
                    + '</tr>';
            }
            h += '</tbody></table>';
            h += '<div class="pm-pager">'
                + '<button class="pm-pg-prev" type="button">上一页</button>'
                + '<span class="pm-pg-info">第 <span class="pm-pg-cur">1</span> / <span class="pm-pg-tot">1</span> 页</span>'
                + '<button class="pm-pg-next" type="button">下一页</button>'
                + '<span class="pm-pg-size">每页 <select class="pm-pg-sz"><option>10</option><option selected>15</option><option>20</option><option>50</option><option>100</option></select> 条</span>'
                + '</div>';
        }
        return h;
    }

    // Attach hover crosshair + tooltip to every .pm-chart inside `$perf`.
    function wirePerfCharts($perf) {
        var W = 800, IH = 140, PL = 40, PR = 10, PT = 10, IW = W - PL - PR;
        function pad2(n) { return n < 10 ? '0' + n : '' + n; }
        function fmtClock(sec) {
            var d = new Date(sec * 1000);
            return pad2(d.getHours()) + ':' + pad2(d.getMinutes()) + ':' + pad2(d.getSeconds());
        }
        function fmtRel(sec) {
            if (sec < 60) return sec.toFixed(1) + 's';
            var m = Math.floor(sec / 60), s = sec - m * 60;
            return m + 'm' + s.toFixed(0) + 's';
        }
        $perf.find('.pm-chart').each(function () {
            var chart = this;
            var svg = chart.querySelector('svg');
            var zone = chart.querySelector('.pm-hv-zone');
            var hover = chart.querySelector('.pm-hover');
            var line = chart.querySelector('.pm-hv-line');
            var dot = chart.querySelector('.pm-hv-dot');
            var tip = chart.querySelector('.pm-tip');
            if (!zone || !hover) return;
            var pts = (chart.getAttribute('data-points') || '').split(',').map(parseFloat).filter(function (v) { return !isNaN(v); });
            if (pts.length < 2) return;
            var color = chart.getAttribute('data-color') || '#3b82f6';
            var duration = parseFloat(chart.getAttribute('data-duration')) || 0;
            var startTs = parseFloat(chart.getAttribute('data-start-ts')) || 0;
            var unit = chart.getAttribute('data-unit') || '';
            var yMin = parseFloat(chart.getAttribute('data-ymin')) || 0;
            var yMax = parseFloat(chart.getAttribute('data-ymax')) || 1;
            function onMove(e) {
                var rect = svg.getBoundingClientRect();
                // map mouse X to viewBox X (0..W)
                var rx = e.clientX - rect.left;
                var vx = rx * (W / rect.width);
                var fx = (vx - PL) / IW;  // 0..1 within data
                if (fx < 0) fx = 0;
                if (fx > 1) fx = 1;
                var idx = Math.round(fx * (pts.length - 1));
                var v = pts[idx];
                var px = PL + (idx / (pts.length - 1)) * IW;
                var py = PT + IH - ((v - yMin) / (yMax - yMin)) * IH;
                line.setAttribute('x1', px);
                line.setAttribute('x2', px);
                dot.setAttribute('cx', px);
                dot.setAttribute('cy', py);
                hover.style.display = '';
                // Tooltip position in pixel space.
                var pxScreen = rect.left + (px / W) * rect.width - rect.left;
                var pyScreen = rect.top + (py / 180) * rect.height - rect.top;
                var tSec = duration > 0 ? (duration * idx / (pts.length - 1)) : idx;
                var tLabel = startTs > 0 ? fmtClock(startTs + tSec) : fmtRel(tSec);
                tip.innerHTML = '<div class="pm-tip-t">' + tLabel + '</div>'
                    + '<div class="pm-tip-v" style="color:' + color + '">'
                    + (Math.abs(v) >= 10 ? v.toFixed(1) : v.toFixed(2)) + (unit ? '<span class="pm-tip-u">' + unit + '</span>' : '')
                    + '</div>';
                tip.style.display = 'block';
                // Position tooltip near cursor but inside chart bounds.
                var tipW = tip.offsetWidth, tipH = tip.offsetHeight;
                var left = pxScreen + 12;
                if (left + tipW > rect.width) left = pxScreen - tipW - 12;
                var top = pyScreen - tipH - 8;
                if (top < 0) top = pyScreen + 12;
                tip.style.left = left + 'px';
                tip.style.top = top + 'px';
            }
            function onLeave() {
                hover.style.display = 'none';
                tip.style.display = 'none';
            }
            zone.addEventListener('mousemove', onMove);
            zone.addEventListener('mouseleave', onLeave);
        });
    }

    // Multi-line chart: toggle visibility on legend click + crosshair tooltip on hover.
    function wireMultiLineCharts($perf) {
        var root = $perf[0] || $perf.get(0);
        var charts = root.querySelectorAll('.pm-mlchart');
        function pad2(n) { return n < 10 ? '0' + n : '' + n; }
        charts.forEach(function (chart) {
            var series;
            try { series = JSON.parse(chart.getAttribute('data-series')); }
            catch (e) { return; }
            var PL = +chart.getAttribute('data-pl'), PT = +chart.getAttribute('data-pt');
            var W = +chart.getAttribute('data-w'), H = +chart.getAttribute('data-h');
            var PR = +chart.getAttribute('data-pr'), PB = +chart.getAttribute('data-pb');
            var IW = W - PL - PR, IH = H - PT - PB;
            var yMin = +chart.getAttribute('data-ymin'), yMax = +chart.getAttribute('data-ymax');
            var duration = +chart.getAttribute('data-duration'), startTs = +chart.getAttribute('data-start-ts');
            var unit = chart.getAttribute('data-unit') || '';
            var maxLen = 0;
            for (var s = 0; s < series.length; s++) {
                if (series[s].pts.length > maxLen) maxLen = series[s].pts.length;
            }
            var hidden = {};
            var hoverG = chart.querySelector('.pm-ml-hover');
            var vline = chart.querySelector('.pm-ml-vline');
            var dots = chart.querySelectorAll('.pm-ml-dot');
            var zone = chart.querySelector('.pm-ml-zone');
            var tip = chart.querySelector('.pm-tip');
            var lines = chart.querySelectorAll('.pm-ml-line');
            var legendItems = chart.parentElement.querySelectorAll('.pm-leg-clk');

            // Legend click → toggle visibility.
            legendItems.forEach(function (it) {
                it.addEventListener('click', function () {
                    var idx = +it.getAttribute('data-idx');
                    hidden[idx] = !hidden[idx];
                    it.classList.toggle('pm-leg-off', !!hidden[idx]);
                    lines[idx].style.display = hidden[idx] ? 'none' : '';
                    dots[idx].style.display = hidden[idx] ? 'none' : '';
                });
            });

            zone.addEventListener('mousemove', function (e) {
                var rect = chart.getBoundingClientRect();
                var scaleX = rect.width / W;
                var mx = (e.clientX - rect.left) / scaleX;
                var ratio = (mx - PL) / IW;
                if (ratio < 0) ratio = 0; if (ratio > 1) ratio = 1;
                var idx = Math.round(ratio * (maxLen - 1));
                hoverG.style.display = '';
                var vx = PL + (idx / (maxLen - 1)) * IW;
                vline.setAttribute('x1', vx);
                vline.setAttribute('x2', vx);
                var rows = [];
                for (var si = 0; si < series.length; si++) {
                    var dot = dots[si];
                    if (hidden[si]) { dot.style.display = 'none'; continue; }
                    var pts = series[si].pts;
                    if (idx >= pts.length) { dot.style.display = 'none'; continue; }
                    var v = pts[idx];
                    var cy = PT + IH - ((v - yMin) / (yMax - yMin)) * IH;
                    dot.setAttribute('cx', vx);
                    dot.setAttribute('cy', cy);
                    dot.style.display = '';
                    rows.push({ name: series[si].name, val: v, color: dot.getAttribute('fill') });
                }
                rows.sort(function (a, b) { return b.val - a.val; });
                var tlbl = '';
                if (duration > 0 && startTs > 0) {
                    var t = startTs + duration * idx / (maxLen - 1);
                    var dd = new Date(t * 1000);
                    tlbl = pad2(dd.getHours()) + ':' + pad2(dd.getMinutes()) + ':' + pad2(dd.getSeconds());
                } else if (duration > 0) {
                    tlbl = (duration * idx / (maxLen - 1)).toFixed(0) + 's';
                }
                var html = '<div class="pm-tip-t">' + tlbl + '</div>';
                for (var r = 0; r < rows.length; r++) {
                    html += '<div class="pm-tip-r">'
                        + '<span class="pm-tip-sw" style="background:' + rows[r].color + '"></span>'
                        + '<span class="pm-tip-nm">' + rows[r].name + '</span>'
                        + '<span class="pm-tip-vv">' + rows[r].val.toFixed(1) + unit + '</span>'
                        + '</div>';
                }
                tip.innerHTML = html;
                tip.style.display = '';
                var tipW = tip.offsetWidth, tipH = tip.offsetHeight;
                var sx = vx / W * rect.width;
                var left = sx + 12;
                if (left + tipW > rect.width) left = sx - tipW - 12;
                var top = 4;
                if (top + tipH > rect.height) top = rect.height - tipH - 4;
                tip.style.left = left + 'px';
                tip.style.top = top + 'px';
            });
            zone.addEventListener('mouseleave', function () {
                hoverG.style.display = 'none';
                tip.style.display = 'none';
            });
        });
    }

    // Attach filter listeners after the anomaly HTML is injected into the DOM.
    function wireAnomalyFilter($body) {
        var $type = $body.find('.pm-flt-type');
        var $pkg = $body.find('.pm-flt-pkg');
        var $tc = $body.find('.pm-flt-tc');
        var $kw = $body.find('.pm-flt-kw');
        var $shown = $body.find('.pm-flt-shown');
        var $rows = $body.find('.pm-tbl-anom tbody tr');
        var $cur = $body.find('.pm-pg-cur');
        var $tot = $body.find('.pm-pg-tot');
        var $sz = $body.find('.pm-pg-sz');
        var $prev = $body.find('.pm-pg-prev');
        var $next = $body.find('.pm-pg-next');
        var page = 1;
        function getPageSize() { return parseInt($sz.val(), 10) || 20; }
        function apply() {
            var t = $type.val() || '';
            var p = $pkg.val() || '';
            var c = $tc.val() || '';
            var k = ($kw.val() || '').toLowerCase().trim();
            var matched = [];
            $rows.each(function () {
                var row = this;
                var ok = (!t || row.getAttribute('data-type') === t)
                    && (!p || row.getAttribute('data-pkg') === p)
                    && (!c || row.getAttribute('data-tc') === c)
                    && (!k || (row.getAttribute('data-kw') || '').indexOf(k) >= 0);
                row.dataset.match = ok ? '1' : '0';
                if (ok) matched.push(row);
            });
            $shown.text(matched.length);
            paginate(matched);
        }
        function paginate(matched) {
            var sz = getPageSize();
            var total = Math.max(1, Math.ceil(matched.length / sz));
            if (page > total) page = total;
            if (page < 1) page = 1;
            var start = (page - 1) * sz;
            var end = start + sz;
            $rows.each(function () { this.style.display = 'none'; });
            for (var i = start; i < Math.min(end, matched.length); i++) {
                matched[i].style.display = '';
            }
            $cur.text(page);
            $tot.text(total);
            $prev.prop('disabled', page <= 1);
            $next.prop('disabled', page >= total);
        }
        $type.on('change', function () { page = 1; apply(); });
        $pkg.on('change', function () { page = 1; apply(); });
        $tc.on('change', function () { page = 1; apply(); });
        $kw.on('input', function () { page = 1; apply(); });
        $sz.on('change', function () { page = 1; apply(); });
        $prev.on('click', function () { page--; apply(); });
        $next.on('click', function () { page++; apply(); });
        $body.find('.pm-flt-clr').on('click', function () {
            $type.val(''); $pkg.val(''); $tc.val(''); $kw.val('');
            page = 1; apply();
        });
        apply();

        // In-page modal viewer for log/screenshot (no new tab). Uses native DOM
        // because jQuery is not exposed globally by Allure.
        function openModal(contentHtml) {
            var prev = document.querySelector('.pm-modal');
            if (prev) prev.remove();
            var m = document.createElement('div');
            m.className = 'pm-modal';
            m.innerHTML = '<div class="pm-modal-bd">'
                + '<button class="pm-modal-x" type="button">×</button>'
                + '<div class="pm-modal-ct">' + contentHtml + '</div></div>';
            function close() {
                m.remove();
                document.removeEventListener('keydown', onKey);
            }
            function onKey(e) { if (e.key === 'Escape') close(); }
            m.addEventListener('click', function (e) { if (e.target === m) close(); });
            m.querySelector('.pm-modal-x').addEventListener('click', close);
            document.addEventListener('keydown', onKey);
            document.body.appendChild(m);
            return m;
        }

        // Log 文件查看: 每次只通过 HTTP Range 读取 256KB，避免大日志一次进内存。
        function openLogModal(lsrc) {
            var mm = openModal(
                '<div class="pm-modal-cap">' + esc(lsrc)
                + ' <a href="' + esc(lsrc) + '" download style="margin-left:8px;font-size:12px">下载完整</a></div>'
                + '<div class="pm-log-info" style="font-size:12px;color:#6b7280;padding:4px 8px">下载中…</div>'
                + '<pre class="pm-log-pre" style="max-height:65vh;overflow:auto;white-space:pre;margin:0"></pre>'
                + '<div class="pm-log-more" style="display:none;text-align:center;padding:8px 0">'
                + '<button class="pm-log-next" type="button" style="margin:0 6px;padding:4px 12px;cursor:pointer">加载下一段</button>'
                + '<button class="pm-log-all" type="button" style="margin:0 6px;padding:4px 12px;cursor:pointer">加载全部剩余</button>'
                + '</div>'
            );
            var pre = mm.querySelector('.pm-log-pre');
            var info = mm.querySelector('.pm-log-info');
            var more = mm.querySelector('.pm-log-more');
            var btnNext = mm.querySelector('.pm-log-next');
            var btnAll = mm.querySelector('.pm-log-all');
            var CHUNK = 256 * 1024;  // 256KB
            var decoder = new TextDecoder('utf-8', { fatal: false });
            var offset = 0;
            var total = null;
            var fullBytes = null;  // 服务器忽略 Range、返回 200 时的兼容缓存
            var busy = false;
            function fmtSz(n) {
                if (n < 1024) return n + ' B';
                if (n < 1048576) return (n / 1024).toFixed(1) + ' KB';
                return (n / 1048576).toFixed(2) + ' MB';
            }
            function updateInfo() {
                if (total == null) {
                    info.textContent = '已加载 ' + fmtSz(offset);
                } else {
                    info.textContent = '已加载 ' + fmtSz(offset) + ' / ' + fmtSz(total)
                        + ' (' + (total ? (offset / total * 100).toFixed(1) : '100.0') + '%)';
                }
                more.style.display = total != null && offset >= total ? 'none' : '';
            }
            function appendBytes(bytes) {
                if (!bytes.length && offset === 0) {
                    pre.textContent = '(空文件)';
                    info.textContent = '0 B';
                    more.style.display = 'none';
                    return;
                }
                var isLast = total != null && offset + bytes.length >= total;
                pre.appendChild(document.createTextNode(
                    decoder.decode(bytes, { stream: !isLast })
                ));
                offset += bytes.length;
                updateInfo();
            }
            function parseTotal(response) {
                var cr = response.headers.get('Content-Range') || '';
                var match = /bytes\s+\d+-\d+\/(\d+|\*)/i.exec(cr);
                if (match && match[1] !== '*') return Number(match[1]);
                var len = response.headers.get('Content-Length');
                return response.status === 200 && len ? Number(len) : null;
            }
            function loadRange(size) {
                if (busy || (total != null && offset >= total)) return;
                busy = true;
                btnNext.disabled = true;
                btnAll.disabled = true;
                info.textContent = '正在读取 ' + fmtSz(offset) + ' 之后的数据…';

                if (fullBytes) {
                    var cachedEnd = Math.min(offset + size, fullBytes.length);
                    appendBytes(fullBytes.subarray(offset, cachedEnd));
                    busy = false;
                    btnNext.disabled = false;
                    btnAll.disabled = false;
                    return;
                }

                var end = offset + Math.max(1, size) - 1;
                if (total != null) end = Math.min(end, total - 1);
                fetch(lsrc, {
                    cache: 'no-store',
                    headers: { Range: 'bytes=' + offset + '-' + end }
                }).then(function (response) {
                    if (!response.ok) throw new Error('HTTP ' + response.status);
                    var discovered = parseTotal(response);
                    if (discovered != null) total = discovered;
                    return response.arrayBuffer().then(function (buf) {
                        return { status: response.status, bytes: new Uint8Array(buf) };
                    });
                }).then(function (result) {
                    var bytes = result.bytes;
                    if (result.status === 200) {
                        // 某些静态服务器忽略 Range；缓存完整响应，后续仍按段渲染。
                        fullBytes = bytes;
                        total = bytes.length;
                        bytes = fullBytes.subarray(offset, Math.min(offset + size, total));
                    } else if (total == null && bytes.length < size) {
                        total = offset + bytes.length;
                    }
                    appendBytes(bytes);
                    if (offset === bytes.length) pre.scrollTop = 0;
                }).catch(function (err) {
                    info.textContent = '加载失败: ' + err.message;
                }).then(function () {
                    busy = false;
                    btnNext.disabled = false;
                    btnAll.disabled = false;
                });
            }
            btnNext.addEventListener('click', function () { loadRange(CHUNK); });
            btnAll.addEventListener('click', function () {
                loadRange(total != null ? Math.max(0, total - offset) : 64 * 1024 * 1024);
            });
            loadRange(CHUNK);
        }
        var bodyEl = $body[0] || $body.get(0);
        bodyEl.addEventListener('click', function (e) {
            var img = e.target.closest('.pm-img-open');
            if (img) {
                var src = img.getAttribute('data-src');
                openModal('<img src="' + esc(src) + '" alt="" style="max-width:100%;max-height:80vh;display:block;margin:auto"/>'
                    + '<div class="pm-modal-cap">' + esc(src) + '</div>');
                return;
            }
            var log = e.target.closest('.pm-log-open');
            if (log) {
                e.preventDefault();
                var lsrc = log.getAttribute('data-src');
                openLogModal(lsrc);
                return;
            }
            var vid = e.target.closest('.pm-vid-open');
            if (vid) {
                e.preventDefault();
                var vsrc = vid.getAttribute('data-src');
                var mm = openModal('<div class="pm-vid-wrap" style="text-align:center;padding:12px;color:#6b7280">加载视频中…</div>'
                    + '<div class="pm-modal-cap">' + esc(vsrc)
                    + ' <a href="' + esc(vsrc) + '" download style="margin-left:8px;font-size:12px">下载</a></div>');
                var wrap = mm.querySelector('.pm-vid-wrap');
                var v = document.createElement('video');
                v.controls = true;
                v.autoplay = true;
                v.preload = 'metadata';
                v.style.cssText = 'max-width:80vw;max-height:75vh;display:block;margin:auto;background:#000';
                v.addEventListener('loadedmetadata', function () {
                    wrap.style.color = '';
                });
                v.addEventListener('error', function () {
                    wrap.textContent = '视频加载失败，请检查资源是否已打包或编码是否受浏览器支持';
                });
                v.src = vsrc;
                wrap.textContent = '';
                wrap.appendChild(v);
            }
        });
    }

    // AppLayout extension: only override `getContentView` so SideNavView still
    // injects (otherwise the tab strip disappears after clicking).
    // Template must be set in onBeforeRender (instance property) because the
    // AppLayout constructor uses _defineProperty to install a default template
    // AFTER initialize, shadowing prototype overrides (Allure 2.25.0).
    var DashboardContent = allure.components.AppLayout.extend({
        className: '',
        regions: {},
        onBeforeRender: function () {
            this.template = function () {
                return '<div class="ac-dash">'
                    + '<div class="ac-split">'
                    + '<div class="ac-col"><div class="ac-perf-body">Loading…</div></div>'
                    + '<div class="ac-col"><div class="ac-anomaly-body">Loading…</div></div>'
                    + '</div></div>';
            };
        },
        onRender: function () {
            var self = this;
            function load(name) {
                return fetch('widgets/' + name + '.json', { cache: 'no-store' })
                    .then(function (r) {
                        if (!r.ok) throw new Error(name + ': HTTP ' + r.status);
                        return r.json();
                    });
            }
            Promise.all([load('perf-monitor'), load('anomaly-monitor')])
                .then(function (results) {
                    var $perf = self.$('.ac-perf-body');
                    $perf.html(renderPerf(results[0]));
                    wirePerfCharts($perf);
                    wireMultiLineCharts($perf);
                    var $anom = self.$('.ac-anomaly-body');
                    $anom.html(renderAnomaly(results[1]));
                    wireAnomalyFilter($anom);
                }).catch(function (err) {
                    var message = '<div class="pm-empty" style="color:#b91c1c">Dashboard 数据加载失败: '
                        + esc(err && err.message ? err.message : err) + '</div>';
                    self.$('.ac-perf-body').html(message);
                    self.$('.ac-anomaly-body').html(message);
                });
        },
        getContentView: function () { return null; }
    });

    var DashboardView = allure.components.AppLayout.extend({
        initialize: function () { this.tabName = 'tab.autocarDashboard.name'; },
        getContentView: function () { return new DashboardContent(); }
    });

    allure.api.addTab('autocar-dashboard', {
        title: 'tab.autocarDashboard.name',
        icon: 'fa fa-tachometer',
        route: 'autocar-dashboard',
        onEnter: function () { return new DashboardView(); }
    });
})();

// ───────────────────────────────────────────────────────────────
//  ThunderSoft brand override
//  Replaces the default "Allure" wordmark + browser tab title with
//  "ThunderSoft". Runs once on plugin load; a MutationObserver keeps
//  the text replaced even when Allure re-renders the side-nav.
// ───────────────────────────────────────────────────────────────
(function () {
    var BRAND = 'ThunderSoft';
    var TITLE = 'ThunderSoft Report';

    function applyBrand() {
        if (document.title !== TITLE) document.title = TITLE;
        // Side-nav brand wordmark (Allure 2.x): .side-nav__brand-name
        var nodes = document.querySelectorAll(
            '.side-nav__brand-name, .side-nav__brand, .app__header .logo, .side-nav__brand-text'
        );
        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].textContent && nodes[i].textContent.trim() !== BRAND) {
                nodes[i].textContent = BRAND;
            }
        }
    }

    applyBrand();
    if (window.MutationObserver) {
        var obs = new MutationObserver(applyBrand);
        obs.observe(document.documentElement, { childList: true, subtree: true });
    } else {
        setInterval(applyBrand, 500);
    }
})();
