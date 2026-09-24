<script>
  import { onMount } from 'svelte';
  import { link } from 'svelte-spa-router';
  import {
    api,
    VAT_QUERY_STATUS_DYEING,
    CHECKS_QUERY_PERIOD_TODAY,
  } from '../lib/api.js';

  let stats = null;
  let error = '';

  onMount(async () => {
    try {
      stats = await api('/dashboard/stats');
    } catch (e) {
      error = e.message;
    }
  });
</script>

<h1 class="page-title">工艺总览</h1>
<p class="page-sub">按染坊 → 染缸 → 染程 → 色牢度推进；顶部步骤条可跳转各工序。</p>

{#if error}
  <p class="err">{error}</p>
{/if}

{#if stats}
  <div class="grid-stats">
    <div class="stat">
      <div class="n">{stats.dyeHouseTotal}</div>
      <div class="l">染坊</div>
    </div>
    <div class="stat">
      <div class="n">{stats.vatReadyCount}</div>
      <div class="l">就绪染缸</div>
    </div>
    <!-- 染程中卡：计数与 /vats 列表 ?status=dyeing 同源（同一状态字面量） -->
    <a
      class="stat stat-link"
      href="/vats?status={VAT_QUERY_STATUS_DYEING}"
      use:link
      title="按「染色中」过滤染缸列表"
    >
      <div class="n">{stats.vatDyeingCount}</div>
      <div class="l">染色中 <span class="go">对照列表 →</span></div>
    </a>
    <div class="stat">
      <div class="n">{stats.lotsLast7d}</div>
      <div class="l">近 7 日染程</div>
    </div>
    <!-- 近一天卡：东八区自然日，与 /checks 列表 ?period=today 同源 -->
    <a
      class="stat stat-link"
      href="/checks?period={CHECKS_QUERY_PERIOD_TODAY}"
      use:link
      title="按东八区今日过滤色牢度抽检列表"
    >
      <div class="n">{stats.checksToday}</div>
      <div class="l">近一天抽检 <span class="go">对照列表 →</span></div>
    </a>
  </div>
{/if}

<div class="panel">
  <p style="margin:0 0 0.75rem;color:var(--indigo-mist);font-size:0.9rem;">
    业务约束：仅当染缸为 <strong>ready</strong> 或 <strong>dyeing</strong> 时可新建染程；新建后染缸自动变为 dyeing。排液可用染缸「完成排液」动作。
  </p>
  <div class="toolbar">
    <a class="btn" href="/houses" use:link>进入染坊</a>
    <a class="btn ghost" href="/vats" use:link>管理染缸</a>
    <a class="btn ghost" href="/lots" use:link>登记染程</a>
    <a class="btn ghost" href="/checks" use:link>色牢度抽检</a>
  </div>
</div>

<style>
  .stat-link {
    display: block;
    cursor: pointer;
    transition:
      transform 0.12s ease,
      border-color 0.12s ease;
  }

  .stat-link:hover {
    transform: translateY(-2px);
    border-color: var(--indigo-bright);
  }

  .go {
    font-size: 0.68rem;
    color: var(--indigo-bright);
    white-space: nowrap;
  }
</style>
