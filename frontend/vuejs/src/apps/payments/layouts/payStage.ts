/**
 * The checkout return stage (PaymentSuccessView, PaymentCancelView): a status
 * mark in the light, a headline, and one card edged like the home page's
 * prompt bar. Both views render inside PaymentLayout's .spotlight root.
 *
 * The spinner and the entrance rise stay in PaymentLayout's <style>, as
 * keyframe animations (`pay-spinner`, `pay-rise`).
 */
export const pay = {
  stage:
    'relative isolate overflow-hidden min-h-screen pt-[calc(3.5rem+clamp(56px,8vw,104px))] pb-[clamp(72px,10vw,120px)]',
  inner: 'max-w-[40rem] mx-auto px-[clamp(16px,4vw,40px)] text-center',
  mark:
    'grid place-items-center w-16 h-16 mx-auto mb-[26px] rounded-[20px] border border-sl-line-strong bg-sl-card-bg [box-shadow:var(--sl-card-shadow),0_0_40px_-8px_var(--sl-glow)] text-[22px]',
  title: 'text-[length:clamp(38px,6vw,64px)] leading-none tracking-[-0.035em]',
  // ! because .spotlight .sl-lede, on the same element, sets margin and size.
  lede: '!mt-[18px] !mx-auto !mb-0 !text-[length:clamp(16px,1.5vw,18.5px)]',
  card:
    'mt-9 p-7 border border-transparent rounded-[22px] [background:var(--sl-prompt-bg)_padding-box,var(--sl-prompt-edge)_border-box] shadow-sl-prompt text-sl-muted text-[16px] leading-[1.6]',
  cardError:
    'mt-9 p-7 border border-transparent rounded-[22px] [background:var(--sl-prompt-bg)_padding-box,linear-gradient(140deg,var(--sl-bad),var(--sl-line)_60%)_border-box] shadow-sl-prompt text-sl-muted text-[16px] leading-[1.6]',
  cardLabel:
    'mt-[22px] pt-[22px] border-t border-t-sl-line text-[11.5px] font-semibold tracking-[0.16em] uppercase text-sl-faint',
  cardValue:
    'mt-2 font-sl-display text-[length:clamp(24px,3vw,32px)] font-extrabold tracking-[-0.025em] text-sl-text',
  actions: 'flex flex-wrap items-center justify-center gap-3 mt-9',
  spinner: 'pay-spinner w-10 h-10 mx-auto rounded-[50%] border-[3px] border-sl-line-strong border-t-sl-coral',
}
