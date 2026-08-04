import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ProductShot from '../media/ProductShot.vue'

/**
 * The home page is mostly imagery, so the two things worth locking down are
 * the ones that quietly regress: every shot must reserve its box before the
 * image lands (no layout shift), and only the above-the-fold shot may opt out
 * of lazy loading.
 */
describe('ProductShot', () => {
  const base = {
    src: '/product/build-workspace.webp',
    alt: 'The Imagi build workspace',
    width: 2400,
    height: 1500,
  }

  const mountWith = (props: object = {}) => mount(ProductShot, { props: { ...base, ...props } })

  it('reserves the intrinsic box so the page does not shift as shots load', () => {
    const img = mountWith().find('img')
    expect(img.attributes('width')).toBe('2400')
    expect(img.attributes('height')).toBe('1500')
  })

  it('always carries the alt text through', () => {
    expect(mountWith().find('img').attributes('alt')).toBe('The Imagi build workspace')
  })

  it('lazy-loads by default', () => {
    const img = mountWith().find('img')
    expect(img.attributes('loading')).toBe('lazy')
    expect(img.attributes('fetchpriority')).toBe('auto')
  })

  it('loads eagerly and at high priority when it is the hero visual', () => {
    const img = mountWith({ eager: true }).find('img')
    expect(img.attributes('loading')).toBe('eager')
    expect(img.attributes('fetchpriority')).toBe('high')
  })

  it('omits the chrome label and the caption unless given one', () => {
    const wrapper = mountWith()
    expect(wrapper.find('.shot__chip').exists()).toBe(false)
    expect(wrapper.find('figcaption').exists()).toBe(false)
  })

  it('renders the chrome label and the caption when given', () => {
    const wrapper = mountWith({ label: 'imagi — build workspace', caption: 'Mid-conversation.' })
    expect(wrapper.find('.shot__chip').text()).toBe('imagi — build workspace')
    expect(wrapper.find('figcaption').text()).toBe('Mid-conversation.')
  })
})
