<script>
  import { onMount } from 'svelte';
  import { link } from 'svelte-spa-router';
  import { api, VAT_STATUS_VALUE } from '../lib/api.js';

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
    <!-- 染程中卡与染缸列表 ?status=dyeing 同源自后端同一字面量，点击即对照 -->
    <a
      class="stat stat-link"
      href={`/vats?status=${VAT_STATUS_VALUE.DYEING}`}
      use:link
      title="查看染程中染缸列表"
    >
      <div class="n">{stats.vatDyeingCount}</div>
      <div class="l">染程中染缸 <span class="go">对照 →</span></div>
    </a>
    <div class="stat">
      <div class="n">{stats.lotsLast7d}</div>
      <div class="l">近 7 日染程</div>
    </div>
    <!-- 今日抽检卡与抽检列表 ?date=today 同源东八区自然日，点击即对照 -->
    <a
      class="stat stat-link"
      href="/checks?date=today"
      use:link
      title="查看今日（东八区自然日）抽检列表"
    >
      <div class="n">{stats.checksTodayCount}</div>
      <div class="l">今日抽检 <span class="go">对照 →</span></div>
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
    text-decoration: none;
    display: block;
    cursor: pointer;
    transition: filter 0.15s ease, border-color 0.15s ease;
  }

  .stat-link:hover {
    filter: brightness(1.15);
    border-color: var(--indigo-bright);
  }

  .go {
    font-size: 0.7rem;
    color: var(--indigo-bright);
    opacity: 0.85;
  }
</style>
