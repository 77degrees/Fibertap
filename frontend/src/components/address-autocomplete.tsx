'use client'

import { useEffect, useRef, useCallback } from 'react'

interface AddressAutocompleteProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
}

export function AddressAutocomplete({
  value,
  onChange,
  placeholder = "Enter address",
  className = "",
}: AddressAutocompleteProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const autocompleteRef = useRef<any>(null)

  const initAutocomplete = useCallback(() => {
    if (!inputRef.current) return

    const google = (window as any).google
    if (!google?.maps?.places) return

    // Initialize autocomplete
    autocompleteRef.current = new google.maps.places.Autocomplete(
      inputRef.current,
      {
        types: ['address'],
        componentRestrictions: { country: 'us' },
        fields: ['formatted_address'],
      }
    )

    // Handle place selection
    autocompleteRef.current.addListener('place_changed', () => {
      const place = autocompleteRef.current?.getPlace()
      if (place?.formatted_address) {
        onChange(place.formatted_address)
      }
    })
  }, [onChange])

  useEffect(() => {
    // Try to init immediately if Google is loaded
    initAutocomplete()

    // Also set up a check for when Google loads
    const checkGoogle = setInterval(() => {
      const google = (window as any).google
      if (google?.maps?.places && !autocompleteRef.current) {
        initAutocomplete()
        clearInterval(checkGoogle)
      }
    }, 500)

    return () => {
      clearInterval(checkGoogle)
      if (autocompleteRef.current) {
        const google = (window as any).google
        google?.maps?.event?.clearInstanceListeners(autocompleteRef.current)
      }
    }
  }, [initAutocomplete])

  return (
    <input
      ref={inputRef}
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className={className}
      autoComplete="off"
    />
  )
}
