<script>
  import { link, location } from 'svelte-spa-router';
  import {
    api,
    toLocalInput,
    fromLocalInput,
    queryParam,
    CHECKS_QUERY_PERIOD_TODAY,
  } from '../lib/api.js';

  let lots = [];
  let rows = [];
  let error = '';
  let form = {
    dyeLotId: '',
    checkedAt: toLocalInput(new Date().toISOString()),
    washFastness: 4,
    rubFastness: 3.5,
    tempC: 40,
    notes: '',
  };
  let editing = null;

  // 列表过滤直接读看板卡跳转写入的同一个 query 字面量（?period=today，东八区自然日）
  $: period = queryParam($location, 'period');
  $: todayOnly = period === CHECKS_QUERY_PERIOD_TODAY;

  async function load() {
    error = '';
    try {
      const qs = todayOnly
        ? `?period=${encodeURIComponent(CHECKS_QUERY_PERIOD_TODAY)}`
        : '';
      [lots, rows] = await Promise.all([api('/dye-lots'), api(`/fastness-checks${qs}`)]);
      if (!form.dyeLotId && lots.length) form.dyeLotId = String(lots[0].id);
    } catch (e) {
      error = e.message;
    }
  }

  // 初始加载 + 看板卡跳入 / 清除过滤时随 query 重新拉取
  $: {
    todayOnly;
    load();
  }

  function lotLabel(id) {
    const lot = lots.find((x) => x.id === id);
    return lot ? `${lot.recipeName} (#${lot.id})` : id;
  }

  async function save() {
    error = '';
    try {
      const body = {
        dyeLotId: Number(form.dyeLotId),
        checkedAt: fromLocalInput(form.checkedAt),
        washFastness: Number(form.washFastness),
        rubFastness: Number(form.rubFastness),
        tempC: Number(form.tempC),
        notes: form.notes.trim() || null,
      };
      if (editing) {
        await api(`/fastness-checks/${editing}`, { method: 'PUT', body: JSON.stringify(body) });
      } else {
        await api('/fastness-checks', { method: 'POST', body: JSON.stringify(body) });
      }
      editing = null;
      form = {
        ...form,
        checkedAt: toLocalInput(new Date().toISOString()),
        notes: '',
      };
      await load();
    } catch (e) {
      error = e.message;
    }
  }

  function startEdit(row) {
    editing = row.id;
    form = {
      dyeLotId: String(row.dyeLotId),
      checkedAt: toLocalInput(row.checkedAt),
      washFastness: row.washFastness,
      rubFastness: row.rubFastness,
      tempC: row.tempC,
      notes: row.notes || '',
    };
  }

  async function remove(id) {
    if (!confirm('确认删除该抽检？')) return;
    error = '';
    try {
      await api(`/fastness-checks/${id}`, { method: 'DELETE' });
      await load();
    } catch (e) {
      error = e.message;
    }
  }
</script>

<h1 class="page-title">色牢度抽检</h1>
<p class="page-sub">耐洗 1–5 级；摩擦牢度须大于 0；记录检测温度。</p>

{#if todayOnly}
  <div class="filter-bar">
    <span>列表过滤：<strong>近一天（东八区今日 00:00 起）</strong>（与看板「近一天抽检」卡同源）</span>
    <a class="btn ghost small" href="/checks" use:link>清除过滤</a>
  </div>
{/if}

<div class="panel" style="margin-bottom:1rem;">
  <div class="form-grid">
    <label
      >染程
      <select bind:value={form.dyeLotId}>
        {#each lots as lot}
          <option value={String(lot.id)}>{lot.recipeName} · {lot.fabricKg}kg</option>
        {/each}
      </select>
    </label>
    <label>检测时间 <input type="datetime-local" bind:value={form.checkedAt} /></label>
    <label>耐洗 (1–5) <input type="number" min="1" max="5" bind:value={form.washFastness} /></label>
    <label>摩擦 (&gt;0) <input type="number" step="0.1" min="0.1" bind:value={form.rubFastness} /></label>
    <label>温度 ℃ <input type="number" step="0.1" bind:value={form.tempC} /></label>
    <label>备注 <input bind:value={form.notes} /></label>
  </div>
  <div class="toolbar">
    <button class="btn" type="button" on:click={save}>{editing ? '保存修改' : '登记抽检'}</button>
    {#if editing}
      <button class="btn ghost" type="button" on:click={() => (editing = null)}>取消</button>
    {/if}
  </div>
  {#if error}<p class="err">{error}</p>{/if}
</div>

<div class="panel">
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>染程</th>
        <th>检测时间</th>
        <th>耐洗</th>
        <th>摩擦</th>
        <th>温度</th>
        <th>备注</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {#each rows as row}
        <tr>
          <td>{row.id}</td>
          <td>{lotLabel(row.dyeLotId)}</td>
          <td>{new Date(row.checkedAt).toLocaleString()}</td>
          <td>{row.washFastness}</td>
          <td>{row.rubFastness}</td>
          <td>{row.tempC}℃</td>
          <td>{row.notes || '—'}</td>
          <td class="row-actions">
            <button class="btn ghost small" type="button" on:click={() => startEdit(row)}>编辑</button>
            <button class="btn danger small" type="button" on:click={() => remove(row.id)}>删除</button>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
