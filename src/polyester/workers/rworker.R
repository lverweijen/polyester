#!/usr/bin/env Rscript

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

get_object_id <- function(id) {
  if (!exists(id, envir = .remote_env, inherits = FALSE)) {
    stop(paste("Object not found:", id))
  }
  get(id, envir = .remote_env, inherits = FALSE)
}

get_function <- function(obj_msg) {
  if (!is.null(obj_msg$name)) {
    # This needs to handle symbols like ::, $, @
    # I don't know how to do this without eval
    eval(parse(text = obj_msg$name), envir = .remote_env)
  } else {
    get_object(obj_msg)
  }
}

get_object <- function(obj_msg) {
  if (!is.null(obj_msg$id)) {
    get_object_id(obj_msg$id)
  } else if (!is.null(obj_msg$name)) {
    get_object_id(obj_msg$name)
  } else if (!is.null(obj_msg$value)) {
    obj_msg$value
  } else {
    stop(paste("Unable to resolve:", msg, "to object."))
  }
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

# TODO By name
handle_get <- function(msg) {
  library(arrow)
  value <- get_object(msg)

  if (is.data.frame(value)) {
      df <- get_object(msg)
      path <- tempfile(fileext = ".arrow")
      write_ipc_stream(df, path)
      list(status="ok", encoding="arrow", path=path)
  } else {
      list(status = "ok", value = value)
  }
}

handle_assign <- function(msg) {
  value <- get_object(msg)
  assign(msg$name, value, envir = .remote_env)
  list(status = "ok")
}

handle_call <- function(msg) {
  fn <- get_function(msg$`function`)
  args <- lapply(c(msg$args, msg$kwargs), get_object)
  result <- do.call(fn, args)
  id <- store_object(result)
  list(status = "ok", id = id)
}

handle_delete <- function(msg) {
  delete_object(msg$id)
  list(status = "ok")
}

handle_insert <- function(msg) {
  # if (!requireNamespace("arrow", quietly = TRUE)) {
  #   stop("arrow package not installed")
  # }

  library(arrow)

  # TODO Handle raw value

  result <- read_ipc_stream(msg$path)
  id <- store_object(result)

  # Clean up
  if (file.exists(msg$path)) {
    unlink(msg$path)
  }

  list(status="ok", id=id)
}

# ----------------------------
# Main loop
# ----------------------------

con_in <- file("stdin", open = "r")
con_out <- stdout()

while (TRUE) {
  line <- readLines(con_in, n = 1, warn = FALSE)
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
      insert = handle_insert(msg),
      stop(paste("Unknown command:", msg$cmd))
    )
    result

  }, error = function(e) {
    list(status = "error", message = as.character(e$message))
  })

  writeLines(toJSON(response, auto_unbox = TRUE), con_out)
  flush(con_out)
}