<script lang="ts">
  import { onMount } from 'svelte';
  import { api, ApiError } from '$lib/api/client';
  import { jobs } from '$lib/stores/jobs.svelte';
  import { accounts } from '$lib/stores/accounts.svelte';
  import { toasts } from '$lib/stores/toasts.svelte';
  import { errorMessage, formatDateTime, formatTimeControl, TIME_CLASS_LABEL } from '$lib/format';
  import { replayPositions, type Replay } from '$lib/chess/replay';
  import { playSound, preloadSounds, soundFor } from '$lib/chess/sounds';
  import { settings } from '$lib/stores/settings.svelte';
  import Board from '$lib/components/Board.svelte';
  import EvalBar from '$lib/components/EvalBar.svelte';
  import EvalGraph from '$lib/components/EvalGraph.svelte';
  import MoveDetail from '$lib/components/MoveDetail.svelte';
  import MoveList, { type MoveCell } from '$lib/components/MoveList.svelte';
  import NavControls from '$lib/components/NavControls.svelte';
  import PlatformBadge from '$lib/components/PlatformBadge.svelte';
  import PlayerRow from '$lib/components/PlayerRow.svelte';
  import ReportCard from '$lib/components/ReportCard.svelte';
  import Button from '$lib/ui/Button.svelte';
  import Card from '$lib/ui/Card.svelte';
  import EmptyState from '$lib/ui/EmptyState.svelte';
  import Icon from '$lib/ui/Icon.svelte';
  import ProgressBar from '$lib/ui/ProgressBar.svelte';
  import Skeleton from '$lib/ui/Skeleton.svelte';
  import type { Analysis, Color, EvalJson, Game } from '$lib/types/api';

  let { id }: { id: string } = $props();
  const gameId = $derived(Number(id));

  let game = $state<Game | null>(null);
  let analysis = $state<Analysis | null>(null);
  let replay = $state<Replay | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let ply = $state(0);
  let orientation = $state<Color>('w');
  let starting = $state(false);

  const total = $derived(replay?.moves.length ?? 0);
  const fen = $derived(replay?.fens[ply] ?? 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1');
  const current = $derived(ply > 0 && analysis ? analysis.moves[ply - 1] ?? null : null);
  const lastMove = $derived(ply > 0 && replay ? ([replay.moves[ply - 1].from, replay.moves[ply - 1].to] as [string, string]) : null);
  const check = $derived.by((): Color | false => {
    if (!replay || ply === 0 || !replay.moves[ply - 1].check) return false;
    return replay.moves[ply - 1].color === 'w' ? 'b' : 'w';
  });
  const evalNow = $derived.by((): EvalJson | null => {
    if (!analysis) return null;
    if (ply === 0) return analysis.moves[0]?.eval_before ?? null;
    return analysis.moves[ply - 1]?.eval_after ?? null;
  });
  const bestArrow = $derived.by((): [string, string] | null => {
    if (!current?.best || current.best.uci === current.uci) return null;
    if (current.classification === 'book' || current.classification === 'forced') return null;
    return [current.best.uci.slice(0, 2), current.best.uci.slice(2, 4)];
  });
  const marker = $derived(current && replay ? { square: replay.moves[ply - 1].to, classification: current.classification } : null);
  const job = $derived(jobs.forGame(gameId));
  const cells = $derived.by((): MoveCell[] => {
    if (!replay) return [];
    return replay.moves.map((m, i) => ({ ply: i + 1, san: m.san, classification: analysis?.moves[i]?.classification }));
  });
  const whiteClock = $derived(clockFor('w'));
  const blackClock = $derived(clockFor('b'));
  const userAccount = $derived(game ? accounts.byId(game.account_id) : undefined);

  function clockFor(color: Color): string | null {
    if (!analysis) return null;
    for (let i = ply - 1; i >= 0; i--) {
      const m = analysis.moves[i];
      if (m.color === color) return m.clock;
    }
    return null;
  }

  async function load() {
    loading = true;
    error = null;
    try {
      game = await api.game(gameId);
      orientation = game.user_color;
      replay = replayPositions(game.pgn);
      try {
        analysis = await api.analysis(gameId);
      } catch (e) {
        if (e instanceof ApiError && e.status === 404) analysis = null;
        else throw e;
      }
      ply = 0;
    } catch (e) {
      error = errorMessage(e);
    } finally {
      loading = false;
    }
  }

  async function reloadAnalysis() {
    try {
      analysis = await api.analysis(gameId);
      game = await api.game(gameId);
      if (ply > total) ply = total;
    } catch (e) {
      toasts.error(errorMessage(e));
    }
  }

  async function analyze(force = false) {
    starting = true;
    try {
      const j = await api.analyze(gameId, force);
      jobs.applyEvent(j);
      if (game) game = { ...game, analysis_status: 'queued' };
    } catch (e) {
      toasts.error(errorMessage(e));
    } finally {
      starting = false;
    }
  }

  const soundOn = $derived(settings.bool('move_sounds'));

  async function setSound(enabled: boolean) {
    try {
      await settings.update({ move_sounds: enabled });
    } catch (e) {
      toasts.error(errorMessage(e));
    }
  }

  /** Move to a ply and play the sound of the move we land on (or the one taken back). */
  function seek(p: number) {
    const next = Math.max(0, Math.min(total, p));
    if (next === ply || !replay || !game) return;
    const landed = next > ply ? replay.moves[next - 1] : replay.moves[ply - 1];
    ply = next;
    if (soundOn && landed) playSound(soundFor(landed, landed.color === game.user_color));
  }

  function onKey(e: KeyboardEvent) {
    if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLSelectElement) return;
    switch (e.key) {
      case 'ArrowLeft': e.preventDefault(); seek(ply - 1); break;
      case 'ArrowRight': e.preventDefault(); seek(ply + 1); break;
      case 'Home': e.preventDefault(); seek(0); break;
      case 'End': e.preventDefault(); seek(total); break;
      case 'f': case 'F': orientation = orientation === 'w' ? 'b' : 'w'; break;
      case 'm': case 'M': setSound(!soundOn); break;
    }
  }

  // When the running job for this game finishes, pull the analysis in.
  let seenDone = false;
  $effect(() => {
    const done = jobs.list.find((j) => j.game_id === gameId && j.kind === 'analyze' && j.status === 'done');
    if (done && !analysis && !seenDone) {
      seenDone = true;
      reloadAnalysis();
    }
    if (!done) seenDone = false;
  });

  onMount(() => {
    load();
    preloadSounds();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });
</script>

<div class="review">
  {#if loading}
    <Skeleton height="28px" width="40%" />
    <div class="layout">
      <Skeleton height="560px" />
      <Skeleton height="560px" />
    </div>
  {:else if error || !game || !replay}
    <EmptyState icon="warning" title="Could not load this game" description={error ?? ''}>
      <Button href="#/games">Back to games</Button>
    </EmptyState>
  {:else}
    <header class="head">
      <a class="back muted" href="#/games"><Icon name="chevron-left" size={14} /> Games</a>
      <div class="title">
        <h1>{game.white} <span class="muted">vs</span> {game.black}</h1>
        <div class="meta muted">
          <span class="res">{game.result}</span>
          {#if game.termination}<span>· {game.termination}</span>{/if}
          <span>· {TIME_CLASS_LABEL[game.time_class]} {formatTimeControl(game.time_control)}</span>
          <span>· {formatDateTime(game.played_at)}</span>
          {#if analysis?.opening_name ?? game.opening_name}<span>· {analysis?.opening_eco ?? game.eco ?? ''} {analysis?.opening_name ?? game.opening_name}</span>{/if}
        </div>
      </div>
      <div class="actions">
        <PlatformBadge platform={game.platform} size="sm" />
        {#if game.url}<Button size="sm" variant="ghost" href={game.url} title="Open on {game.platform === 'chesscom' ? 'Chess.com' : 'Lichess'}"><Icon name="external" size={14} /></Button>{/if}
        {#if analysis}
          <Button size="sm" variant="ghost" onclick={() => analyze(true)} loading={starting} disabled={!!job} title="Re-analyse with current engine settings"><Icon name="sync" size={14} />Re-analyse</Button>
        {/if}
      </div>
    </header>

    <div class="layout">
      <section class="left">
        <div class="stage" class:with-eval={!!analysis}>
          <div class="top">
            <PlayerRow
              name={orientation === 'w' ? game.black : game.white}
              rating={orientation === 'w' ? game.black_rating : game.white_rating}
              color={orientation === 'w' ? 'b' : 'w'}
              clock={orientation === 'w' ? blackClock : whiteClock}
              active={fen.split(' ')[1] === (orientation === 'w' ? 'b' : 'w') && ply < total}
              isUser={game.user_color !== orientation}
              accuracy={analysis ? (orientation === 'w' ? analysis.accuracy_black : analysis.accuracy_white) : null}
            />
          </div>
          {#if analysis}
            <div class="eval"><EvalBar value={evalNow} {orientation} /></div>
          {/if}
          <div class="board">
            <Board {fen} {orientation} {lastMove} {check} bestMove={bestArrow} {marker} />
          </div>
          <div class="bottom">
            <PlayerRow
              name={orientation === 'w' ? game.white : game.black}
              rating={orientation === 'w' ? game.white_rating : game.black_rating}
              color={orientation}
              clock={orientation === 'w' ? whiteClock : blackClock}
              active={fen.split(' ')[1] === orientation && ply < total}
              isUser={game.user_color === orientation}
              accuracy={analysis ? (orientation === 'w' ? analysis.accuracy_white : analysis.accuracy_black) : null}
            />
          </div>
          <div class="nav">
            <NavControls {ply} {total} sound={soundOn} onseek={seek} onsound={setSound} onflip={() => (orientation = orientation === 'w' ? 'b' : 'w')} />
          </div>
        </div>
      </section>

      <section class="right">
        {#if analysis}
          <Card padded={false}>
            <div class="pad"><EvalGraph moves={analysis.moves} {ply} onseek={seek} /></div>
          </Card>
          <Card padded={false}>
            <div class="pad"><MoveDetail record={current} /></div>
          </Card>
          <Card padded={false} class="moves">
            <MoveList moves={cells} {ply} onseek={seek} />
          </Card>
          <Card title="Game report">
            <ReportCard {analysis} {game} />
          </Card>
        {:else}
          <Card>
            {#if job}
              <div class="analyzing">
                <div class="row"><Icon name="sparkle" size={16} /><strong>{job.status === 'queued' ? 'Waiting for the engine…' : 'Analysing…'}</strong></div>
                <ProgressBar value={job.progress} max={job.total} />
                <span class="muted small">{job.total ? `${job.progress} / ${job.total} moves` : 'Queued behind other games'}</span>
              </div>
            {:else if game.analysis_status === 'failed'}
              <div class="analyzing">
                <div class="row"><Icon name="warning" size={16} /><strong>Analysis failed</strong></div>
                <span class="muted small">Check the engine in Settings, then try again.</span>
                <div><Button variant="primary" onclick={() => analyze(true)} loading={starting}>Retry</Button></div>
              </div>
            {:else}
              <div class="analyzing">
                <div class="row"><Icon name="sparkle" size={16} /><strong>Not analysed yet</strong></div>
                <span class="muted small">Run Stockfish over every move to get classifications, accuracy and best lines. {userAccount ? '' : ''}</span>
                <div><Button variant="primary" onclick={() => analyze()} loading={starting}><Icon name="play" size={14} />Analyse game</Button></div>
              </div>
            {/if}
          </Card>
          <Card padded={false} class="moves">
            <MoveList moves={cells} {ply} onseek={seek} />
          </Card>
        {/if}
      </section>
    </div>
  {/if}
</div>

<style>
  .review { display: grid; gap: var(--sp-3); }
  .head { display: grid; grid-template-columns: auto 1fr auto; gap: var(--sp-4); align-items: center; }
  .back { display: inline-flex; align-items: center; gap: 2px; font-size: var(--fs-sm); }
  .title h1 { font-size: var(--fs-xl); }
  .meta { font-size: var(--fs-xs); display: flex; flex-wrap: wrap; gap: 4px; margin-top: 2px; }
  .res { font-weight: 600; color: var(--text); }
  .actions { display: flex; align-items: center; gap: var(--sp-2); }

  /* Board is the hero: it takes all the width it can, capped by the viewport height. */
  .layout {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 380px;
    gap: var(--sp-4);
    align-items: start;
  }
  .left { min-width: 0; display: grid; justify-items: center; }
  .stage {
    --chrome: 250px; /* header + player rows + nav + page padding */
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    grid-template-rows: auto minmax(0, 1fr) auto auto;
    grid-template-areas: "top" "board" "bottom" "nav";
    row-gap: 4px;
    column-gap: var(--sp-2);
    width: min(100%, calc(100vh - var(--chrome)));
  }
  .stage.with-eval {
    grid-template-columns: 22px minmax(0, 1fr);
    grid-template-areas: ". top" "eval board" ". bottom" ". nav";
    width: min(100%, calc(100vh - var(--chrome) + 30px));
  }
  .top { grid-area: top; }
  .eval { grid-area: eval; display: flex; }
  .board { grid-area: board; min-width: 0; }
  .bottom { grid-area: bottom; }
  .nav { grid-area: nav; }

  .right { display: grid; gap: var(--sp-3); min-width: 0; }
  .pad { padding: var(--sp-3); }
  .right :global(.moves) { max-height: 42vh; display: flex; }
  .right :global(.moves .body) { flex: 1; min-height: 0; display: flex; }
  .right :global(.moves .list) { flex: 1; }
  .analyzing { display: grid; gap: var(--sp-3); }
  .row { display: flex; align-items: center; gap: 8px; }
  .small { font-size: var(--fs-xs); }
  @media (max-width: 1100px) {
    .layout { grid-template-columns: minmax(0, 1fr) 340px; }
  }
  @media (max-width: 900px) {
    .layout { grid-template-columns: 1fr; }
    .head { grid-template-columns: 1fr; gap: var(--sp-2); }
    .stage, .stage.with-eval { width: 100%; }
  }
</style>
