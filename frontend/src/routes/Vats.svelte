<script>
  import { link, querystring } from 'svelte-spa-router';
  import { api, VAT_STATUS, VAT_STATUS_VALUE } from '../lib/api.js';

  let houses = [];
  let rows = [];
  let error = '';
  let form = {
    dyeHouseId: '',
    vatCode: '',
    fiberType: '棉',
    capacityL: 500,
    status: VAT_STATUS_VALUE.READY,
  };
  let editing = null;

  // 列表过滤状态来自 URL query（与看板卡片跳转同一参数、同一字面量常量）。
  $: statusFilter = new URLSearchParams($querystring || '').get('status');

  const FILTERS = [
    { value: '', label: '全部' },
    { value: VAT_STATUS_VALUE.READY, label: VAT_STATUS[VAT_STATUS_VALUE.READY] },
    { value: VAT_STATUS_VALUE.DYEING, label: VAT_STATUS[VAT_STATUS_VALUE.DYEING] },
    { value: VAT_STATUS_VALUE.DRAIN, label: VAT_STATUS[VAT_STATUS_VALUE.DRAIN] },
  ];

  async function load() {
    error = '';
    try {
      const qs = statusFilter ? `?status=${encodeURIComponent(statusFilter)}` : '';
      [houses, rows] = await Promise.all([api('/dye-houses'), api(`/vats${qs}`)]);
      if (!form.dyeHouseId && houses.length) form.dyeHouseId = String(houses[0].id);
    } catch (e) {
      error = e.message;
    }
  }

  // 看板卡片跳转或切换筛选时按同一口径重新拉取（首次也会执行）。
  $: {
    void statusFilter;
    load();
  }

  function houseName(id) {
    return houses.find((h) => h.id === id)?.name || id;
  }

  async function save() {
    error = '';
    try {
      const body = {
        dyeHouseId: Number(form.dyeHouseId),
        vatCode: form.vatCode.trim(),
        fiberType: form.fiberType.trim(),
        capacityL: Number(form.capacityL),
        status: form.status,
      };
      if (editing) {
        await api(`/vats/${editing}`, { method: 'PUT', body: JSON.stringify(body) });
      } else {
        await api('/vats', { method: 'POST', body: JSON.stringify(body) });
      }
      editing = null;
      form = {
        dyeHouseId: form.dyeHouseId,
        vatCode: '',
        fiberType: '棉',
        capacityL: 500,
        status: VAT_STATUS_VALUE.READY,
      };
      await load();
    } catch (e) {
      error = e.message;
    }
  }

  function startEdit(row) {
    editing = row.id;
    form = {
      dyeHouseId: String(row.dyeHouseId),
      vatCode: row.vatCode,
      fiberType: row.fiberType,
      capacityL: row.capacityL,
      status: row.status,
    };
  }

  async function drain(id) {
    error = '';
    try {
      await api(`/vats/${id}/drain`, { method: 'POST' });
      await load();
    } catch (e) {
      error = e.message;
    }
  }

  async function remove(id) {
    if (!confirm('确认删除该染缸？')) return;
    error = '';
    try {
      await api(`/vats/${id}`, { method: 'DELETE' });
      await load();
    } catch (e) {
      error = e.message;
    }
  }
</script>

<h1 class="page-title">染缸</h1>
<p class="page-sub">状态：就绪 / 染色中 / 排液。容量单位为升。</p>

<div class="panel" style="margin-bottom:1rem;">
  <div class="form-grid">
    <label
      >所属染坊
      <select bind:value={form.dyeHouseId}>
        {#each houses as h}
          <option value={String(h.id)}>{h.name}</option>
        {/each}
      </select>
    </label>
    <label>缸号 <input bind:value={form.vatCode} /></label>
    <label>纤维类型 <input bind:value={form.fiberType} /></label>
    <label>容量 (L) <input type="number" step="0.1" bind:value={form.capacityL} /></label>
    <label
      >状态
      <select bind:value={form.status}>
        {#each FILTERS.filter((f) => f.value) as f}
          <option value={f.value}>{f.label}</option>
        {/each}
      </select>
    </label>
  </div>
  <div class="toolbar">
    <button class="btn" type="button" on:click={save}>{editing ? '保存修改' : '新建染缸'}</button>
    {#if editing}
      <button
        class="btn ghost"
        type="button"
        on:click={() => {
          editing = null;
        }}>取消</button
      >
    {/if}
  </div>
  {#if error}<p class="err">{error}</p>{/if}
</div>

<div class="panel">
  <div class="toolbar">
    <span class="filter-label">状态筛选</span>
    {#each FILTERS as f}
      <a
        class="btn small ghost chip"
        class:on={statusFilter === f.value || (!statusFilter && f.value === '')}
        href={f.value ? `/vats?status=${f.value}` : '/vats'}
        use:link
      >
        {f.label}
      </a>
    {/each}
    <span class="count-hint">当前 {rows.length} 缸{statusFilter ? `（${VAT_STATUS[statusFilter] || statusFilter}）` : ''}</span>
  </div>
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>染坊</th>
        <th>缸号</th>
        <th>纤维</th>
        <th>容量 L</th>
        <th>状态</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {#each rows as row}
        <tr>
          <td>{row.id}</td>
          <td>{houseName(row.dyeHouseId)}</td>
          <td>{row.vatCode}</td>
          <td>{row.fiberType}</td>
          <td>{row.capacityL}</td>
          <td><span class="badge {row.status}">{VAT_STATUS[row.status] || row.status}</span></td>
          <td class="row-actions">
            {#if row.status !== VAT_STATUS_VALUE.DRAIN}
              <button class="btn ghost small" type="button" on:click={() => drain(row.id)}>完成排液</button>
            {/if}
            <button class="btn ghost small" type="button" on:click={() => startEdit(row)}>编辑</button>
            <button class="btn danger small" type="button" on:click={() => remove(row.id)}>删除</button>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
