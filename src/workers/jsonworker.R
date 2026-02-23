#!/usr/bin/env Rscript

# I don't know R. I generated this using chatgpt.
# I hope it doesn't format my hard drive, lol :-P

suppressMessages({
  library(jsonlite)
  library(uuid)
})

# ----------------------------
# Remote object storage
# ----------------------------

# emptyenv()	niets
# baseenv()	base R functies
# globalenv()	alles wat user geladen heeft
# .remote_env <- new.env(parent = emptyenv())
# .remote_env <- new.env(parent = emptyenv())
.remote_env <- new.env(parent = globalenv())

generate_id <- function() {
  paste0(".", UUIDgenerate())
}

store_object <- function(value) {
  id <- generate_id()
  assign(id, value, envir = .remote_env)
  return(id)
}

get_object <- function(id) {
  if (!exists(id, envir = .remote_env, inherits = FALSE)) {
    stop(paste("Object not found:", id))
  }
  get(id, envir = .remote_env, inherits = FALSE)
}

delete_object <- function(id) {
  if (exists(id, envir = .remote_env, inherits = FALSE)) {
    rm(list = id, envir = .remote_env)
  }
  TRUE
}

# ----------------------------
# Command handlers
# ----------------------------

handle_eval <- function(msg) {
  value <- eval(parse(text = msg$code), envir = .remote_env)
  id <- store_object(value)
  list(status = "ok", id = id)
}

handle_exec <- function(msg) {
  eval(parse(text = msg$code), envir = .remote_env)
  list(status = "ok")
}

handle_get <- function(msg) {
  value <- get_object(msg$id)
  list(status = "ok", value = value)
}

handle_assign <- function(msg) {
  value <- get_object(msg$id)
  assign(msg$name, value, envir = .remote_env)
  list(status = "ok")
}

handle_call <- function(msg) {
  fn <- match.fun(msg$`function`)

  args <- lapply(msg$args, function(arg) {
    if (is.list(arg) && !is.null(arg$ref)) {
      get_object(arg$ref)
    } else {
      arg
    }
  })

  result <- do.call(fn, args)
  id <- store_object(result)

  list(status = "ok", id = id)
}

handle_delete <- function(msg) {
  delete_object(msg$id)
  list(status = "ok")
}

# For big dataframes
handle_export_arrow <- function(msg) {
  library(arrow)

  df <- get_object(msg$id)

  path <- tempfile(fileext = ".arrow")
  write_ipc_stream(df, path)

  list(status="ok", path=path)
}

# ----------------------------
# Main loop
# ----------------------------

con_in <- file("stdin", open = "r")
con_out <- stdout()

while (TRUE) {
    # print('start reading')
  line <- readLines(con_in, n = 1, warn = FALSE)
  # print(line)

  # if (length(line) == 0) {
  #   # Sys.sleep(0.01)
  #   next
  # }
  if (length(line) == 0) break;

  response <- tryCatch({
    msg <- fromJSON(line, simplifyVector = FALSE)

    result <- switch(
      msg$cmd,
      eval   = handle_eval(msg),
      exec   = handle_exec(msg),
      get    = handle_get(msg),
      assign = handle_assign(msg),
      call   = handle_call(msg),
      delete = handle_delete(msg),
      export_arrow = handle_export_arrow(msg),
      stop(paste("Unknown command:", msg$cmd))
    )

    result

  }, error = function(e) {
    list(status = "error", message = as.character(e$message))
  })

  writeLines(toJSON(response, auto_unbox = TRUE), con_out)
  flush(con_out)
}